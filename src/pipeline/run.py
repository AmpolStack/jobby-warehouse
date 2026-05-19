import logging
from .orchestrator import ETLOrchestrator
from .topics import TOPICS, TRANSFORMATIONS
from .loaders.clickhouse import get_clickhouse_client
import pandas as pd
from rich.console import Console
from rich.logging import RichHandler
from rich.theme import Theme

custom_theme = Theme({
    "logging.level.info": "#ccd9a3",
    "logging.level.warning": "#d9c5a3",
    "logging.level.error": "#d9a3a3",
})

console = Console(theme=custom_theme)

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console, rich_tracebacks=True, markup=True)]
)
logger = logging.getLogger(__name__)

def insert_df(client, df: pd.DataFrame, table: str) -> bool:
    if df.empty:
        return True
    return client.insert(df, table)

def main():
    try:
        orchestrator = ETLOrchestrator(TRANSFORMATIONS)
        transformed_tables = orchestrator.run(TOPICS)
        
        client = get_clickhouse_client()
        if client is None:
            logger.error("ClickHouse client unavailable. Cannot load data.")
            return
            
        all_success = True
        for table_name, df in transformed_tables.items():
            success = insert_df(client, df, table_name)
            if not success:
                all_success = False
        
        # Archive processed files only if everything was successful
        if all_success and orchestrator.s3_client and orchestrator.s3_client.extracted_files:
            orchestrator.s3_client.archive_files(orchestrator.s3_client.extracted_files)
            orchestrator.s3_client.extracted_files.clear()
            logger.info("All files archived successfully.")
        elif not all_success:
            logger.warning("Some inserts failed. Files will not be archived.")
            
        logger.info(f"Successfully loaded {len(transformed_tables)} tables")
    except Exception as e:
        logger.error(f"Unexpected error in ETL pipeline: {e}")

if __name__ == "__main__":
    main()