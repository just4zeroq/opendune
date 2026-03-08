"""
配置管理模块
使用 Pydantic Settings 管理应用配置
"""

import os
from functools import lru_cache
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置类"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # 应用配置
    app_name: str = Field(default="OpenDune", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=False, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # API服务
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    api_workers: int = Field(default=4, alias="API_WORKERS")

    # Kafka配置
    kafka_bootstrap_servers: str = Field(
        default="localhost:9092", alias="KAFKA_BOOTSTRAP_SERVERS"
    )
    kafka_client_id: str = Field(default="opendune", alias="KAFKA_CLIENT_ID")
    kafka_group_id: str = Field(default="opendune-group", alias="KAFKA_GROUP_ID")

    @field_validator("kafka_bootstrap_servers")
    @classmethod
    def parse_kafka_servers(cls, v: str) -> List[str]:
        """解析Kafka服务器列表"""
        return [s.strip() for s in v.split(",")]

    # MySQL配置
    mysql_host: str = Field(default="localhost", alias="MYSQL_HOST")
    mysql_port: int = Field(default=3306, alias="MYSQL_PORT")
    mysql_user: str = Field(default="root", alias="MYSQL_USER")
    mysql_password: str = Field(default="root", alias="MYSQL_PASSWORD")
    mysql_database: str = Field(default="opendune", alias="MYSQL_DATABASE")
    mysql_pool_size: int = Field(default=10, alias="MYSQL_POOL_SIZE")

    @property
    def mysql_url(self) -> str:
        """生成MySQL连接URL"""
        return (
            f"mysql+aiomysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        )

    # Doris配置
    doris_host: str = Field(default="localhost", alias="DORIS_HOST")
    doris_port: int = Field(default=9030, alias="DORIS_PORT")
    doris_user: str = Field(default="root", alias="DORIS_USER")
    doris_password: str = Field(default="", alias="DORIS_PASSWORD")
    doris_database: str = Field(default="analytics", alias="DORIS_DATABASE")

    # TDengine配置
    tdengine_host: str = Field(default="localhost", alias="TDENGINE_HOST")
    tdengine_port: int = Field(default=6030, alias="TDENGINE_PORT")
    tdengine_user: str = Field(default="root", alias="TDENGINE_USER")
    tdengine_password: str = Field(default="taosdata", alias="TDENGINE_PASSWORD")
    tdengine_database: str = Field(default="crypto", alias="TDENGINE_DATABASE")

    # Redis配置
    redis_host: str = Field(default="localhost", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_password: Optional[str] = Field(default=None, alias="REDIS_PASSWORD")
    redis_db: int = Field(default=0, alias="REDIS_DB")

    # Alchemy配置
    alchemy_api_key: str = Field(default="", alias="ALCHEMY_API_KEY")
    alchemy_chains: str = Field(default="ethereum", alias="ALCHEMY_CHAINS")
    alchemy_networks: str = Field(default="mainnet", alias="ALCHEMY_NETWORKS")

    @field_validator("alchemy_chains")
    @classmethod
    def parse_chains(cls, v: str) -> List[str]:
        """解析链列表"""
        return [c.strip().lower() for c in v.split(",")]

    # BSC节点配置
    bsc_rpc_url: str = Field(
        default="https://bsc-dataseed.binance.org", alias="BSC_RPC_URL"
    )
    bsc_backup_rpc_urls: str = Field(default="", alias="BSC_BACKUP_RPC_URLS")

    @field_validator("bsc_backup_rpc_urls")
    @classmethod
    def parse_backup_urls(cls, v: str) -> List[str]:
        """解析备份RPC URL列表"""
        if not v:
            return []
        return [u.strip() for u in v.split(",")]

    # 交易所API配置
    binance_api_key: str = Field(default="", alias="BINANCE_API_KEY")
    binance_secret_key: str = Field(default="", alias="BINANCE_SECRET_KEY")
    binance_testnet: bool = Field(default=False, alias="BINANCE_TESTNET")

    okx_api_key: str = Field(default="", alias="OKX_API_KEY")
    okx_secret_key: str = Field(default="", alias="OKX_SECRET_KEY")
    okx_passphrase: str = Field(default="", alias="OKX_PASSPHRASE")
    okx_testnet: bool = Field(default=False, alias="OKX_TESTNET")

    bybit_api_key: str = Field(default="", alias="BYBIT_API_KEY")
    bybit_secret_key: str = Field(default="", alias="BYBIT_SECRET_KEY")
    bybit_testnet: bool = Field(default=False, alias="BYBIT_TESTNET")

    bitget_api_key: str = Field(default="", alias="BITGET_API_KEY")
    bitget_secret_key: str = Field(default="", alias="BITGET_SECRET_KEY")
    bitget_passphrase: str = Field(default="", alias="BITGET_PASSPHRASE")

    # Flink配置
    flink_job_manager_host: str = Field(
        default="localhost", alias="FLINK_JOB_MANAGER_HOST"
    )
    flink_job_manager_port: int = Field(default=8081, alias="FLINK_JOB_MANAGER_PORT")
    flink_parallelism: int = Field(default=4, alias="FLINK_PARALLELISM")
    flink_checkpoint_interval: int = Field(
        default=60000, alias="FLINK_CHECKPOINT_INTERVAL"
    )

    # JWT配置
    jwt_secret: str = Field(default="secret", alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_expiration_hours: int = Field(default=24, alias="JWT_EXPIRATION_HOURS")

    # 速率限制
    rate_limit_requests_per_minute: int = Field(
        default=60, alias="RATE_LIMIT_REQUESTS_PER_MINUTE"
    )

    def is_production(self) -> bool:
        """检查是否为生产环境"""
        return self.app_env.lower() == "production"


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


# 全局配置实例
settings = get_settings()
