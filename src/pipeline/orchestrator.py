from .extractors.s3 import get_s3_client
from typing import Dict, Optional
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class ETLOrchestrator:
    def __init__(self, transformations: list):
        self.s3_client = get_s3_client()
        self.transformations = transformations
    
    def extract_all(self, topics: Dict[str, any]) -> Dict[str, Optional[pd.DataFrame]]:
        raw_data = {}
        if self.s3_client is None:
            logger.error("S3 client is not available. Skipping extraction.")
            return raw_data
            
        for key, config in topics.items():
            logger.info(f"Extracting {config.display_name}...")
            try:
                df = self.s3_client.extract_topic(key, config)
                raw_data[key] = df
                if df is not None:
                    logger.info(f"Extracted {len(df)} rows")
                else:
                    logger.warning(f"No data for {key}")
            except Exception as e:
                logger.error(f"Error extracting topic {key}: {e}")
                raw_data[key] = None
        return raw_data
    
    def transform_all(self, raw_data: Dict[str, Optional[pd.DataFrame]]) -> Dict[str, pd.DataFrame]:
        results = {}
        
        for transformation in self.transformations:
            args = []
            missing = []
            
            for dep in transformation.dependencies:
                if dep in raw_data and raw_data[dep] is not None and not raw_data[dep].empty:
                    args.append(raw_data[dep])
                else:
                    missing.append(dep)
            
            if missing:
                logger.warning(f"Skipping {transformation.table}: missing {missing}")
                continue
            
            try:
                logger.info(f"Building {transformation.table}...")
                df = transformation.builder_func(*args)
                
                if df is not None and not df.empty:
                    results[transformation.table] = df
                    logger.info(f"Built {transformation.table}: {len(df)} rows")
            except Exception as e:
                logger.error(f"Error building {transformation.table}: {e}")
        
        return results
    
    def run(self, topics: Dict[str, any]) -> Dict[str, pd.DataFrame]:
        logger.info("Starting ETL Pipeline")
        raw_data = self.extract_all(topics)
        transformed = self.transform_all(raw_data)
        logger.info(f"ETL Pipeline completed. Built {len(transformed)} tables")
        return transformed