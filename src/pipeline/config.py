import os
from dataclasses import dataclass

@dataclass
class ClickHouseConfig:
    host: str = os.getenv("CH_HOST", "localhost")
    port: int = int(os.getenv("CH_PORT", "9002"))
    user: str = os.getenv("CH_USER", "root")
    password: str = os.getenv("CH_PASSWORD", "root")
    database: str = os.getenv("CH_DATABASE", "warehouse")

@dataclass
class S3Config:
    endpoint: str = os.getenv("S3_ENDPOINT", "http://localhost:9000")
    access_key: str = os.getenv("S3_ACCESS_KEY", "rustfsadmin")
    secret_key: str = os.getenv("S3_SECRET_KEY", "rustfsadmin")
    bucket: str = os.getenv("S3_BUCKET", "data-lake")
    use_ssl: bool = os.getenv("S3_USE_SSL", "False").lower() == "true"

CLICKHOUSE = ClickHouseConfig()
S3 = S3Config()

TENANT_ID_BASES = {
    "product":   {1: 5000, 2: 7000, 3: 8000},
    "customer":  {1: 10000, 2: 20000, 3: 30000},
    "employee":  {1: 2000, 2: 4000, 3: 5000},
    "sectional": {1: 300, 2: 600, 3: 800},
}