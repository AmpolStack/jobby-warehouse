from clickhouse_driver import Client
import pandas as pd
from ..config import CLICKHOUSE
import logging

logger = logging.getLogger(__name__)

class ClickHouseClient:
    def __init__(self):
        self.client = Client(
            host=CLICKHOUSE.host,
            port=CLICKHOUSE.port,
            user=CLICKHOUSE.user,
            password=CLICKHOUSE.password,
            database=CLICKHOUSE.database
        )
        self.database = CLICKHOUSE.database
    
    def execute(self, query: str) -> pd.DataFrame:
        """Execute a query and return a DataFrame"""
        try:
            data, columns = self.client.execute(query, with_column_types=True)
            col_names = [col[0] for col in columns]
            return pd.DataFrame(data, columns=col_names)
        except Exception as e:
            logger.error(f"ClickHouse execute error: {e}")
            return pd.DataFrame()
    
    def insert(self, df: pd.DataFrame, table: str) -> bool:
        """Insert a DataFrame into a table"""
        if df.empty:
            logger.warning(f"No data for table {table}")
            return True
        records = df.to_dict('records')
        try:
            self.client.execute(f'INSERT INTO {self.database}.{table} VALUES', records)
            logger.info(f"Successfully inserted {len(records)} rows into {table}")
            return True
        except Exception as e:
            logger.error(f"ClickHouse insert error for table {table}: {e}")
            return False
    
    def truncate(self, table: str) -> bool:
        """Truncate a table"""
        try:
            self.client.execute(f"TRUNCATE TABLE {self.database}.{table}")
            logger.info(f"Truncated table {table}")
            return True
        except Exception as e:
            logger.warning(f"Could not truncate table {table}: {e}")
            return False

    def close(self):
        self.client.disconnect()

# Singleton
_clickhouse_client = None

def get_clickhouse_client() -> ClickHouseClient:
    global _clickhouse_client
    if _clickhouse_client is None:
        try:
            _clickhouse_client = ClickHouseClient()
        except Exception as e:
            logger.error(f"Failed to initialize ClickHouse client: {e}")
            return None
    return _clickhouse_client