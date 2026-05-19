from s3fs import S3FileSystem
import logging
import json
from datetime import datetime, timezone
from ..config import S3
import pandas as pd

logger = logging.getLogger(__name__)

class S3Client:
    def __init__(self):
        self.fs = S3FileSystem(
            key=S3.access_key,
            secret=S3.secret_key,
            client_kwargs={'endpoint_url': S3.endpoint},
            use_ssl=S3.use_ssl,
        )
        self.extracted_files = []
    
    def list_json_files(self, topic : str):
        """Lists all JSON files within topic path"""
        path = f"{S3.bucket}/topics/{topic}/"
        archived_path = f"{S3.bucket}/topics/processed/{topic}/"
        files = []
        try:
            if self.fs.exists(path):
                files.extend(self.fs.glob(f"{path}**/*.json"))
            logger.info(f"Found {len(files)} new files for {topic}")
            return files
        except Exception as e:
            logger.error(f"Error accessing S3 for topic {topic}: {e}")
            return []
    
    def _convert_mongo_types(self, obj):
        if isinstance(obj, dict):
            if "$oid" in obj:
                return str(obj["$oid"])
            elif "$date" in obj:
                val = obj["$date"]
                if isinstance(val, (int, float)):
                    return datetime.fromtimestamp(val / 1000.0, tz=timezone.utc)
                return datetime.fromisoformat(val.replace('Z', '+00:00'))
            return {k: self._convert_mongo_types(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_mongo_types(v) for v in obj]
        return obj
    
    def read_json_files(self, files):
        records = []
        for file in files:
            try:
                with self.fs.open(file, 'r') as f:
                    for line in f:
                        try:
                            msg = json.loads(line)
                            if 'after' in msg and msg['after'] is not None:
                                record = msg['after']
                                # Detect if source is MongoDB (after is a JSON string)
                                if msg.get('source', {}).get('connector') == 'mongodb' and isinstance(record, str):
                                    record = json.loads(record)
                                    record = self._convert_mongo_types(record)
                                records.append(record)
                            elif 'after' not in msg:
                                records.append(msg)
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse line from {file}")
                            continue
            except Exception as e:
                logger.error(f"Error reading S3 file {file}: {e}")
                continue
        logger.info(f"Extracted {len(records)} records from {len(files)} files")
        return records
    
    def archive_files(self, files: list[str], archive_prefix: str = "processed/"):
        """Move processed files to archive folder without overwriting"""
        import uuid
        from datetime import datetime
        for file in files:
            if "processed/" in file:
                continue
            
            # Generate unique suffix to prevent overwriting historical files
            unique_suffix = f"_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}.json"
            
            archive_path = file.replace("topics/", f"topics/{archive_prefix}")
            archive_path = archive_path.replace(".json", unique_suffix)
            
            self.fs.mv(file, archive_path)
            logger.info(f"Archived: {file} -> {archive_path}")

    def extract_topic(self, topic: str, config) -> pd.DataFrame:
        files = self.list_json_files(config.topic)
        if not files:
            return None
        records = self.read_json_files(files)
        if not records:
            return None
        self.extracted_files.extend(files)
        return pd.DataFrame(records)

# Singleton
_s3_client = None

def get_s3_client() -> S3Client:
    global _s3_client
    if _s3_client is None:
        try:
            _s3_client = S3Client()
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {e}")
            return None
    return _s3_client