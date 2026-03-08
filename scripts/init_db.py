"""
数据库初始化脚本
创建MySQL、Doris、TDengine的表结构
"""

import asyncio
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pymysql
from src.common.config import settings
from src.common.logger import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)


# MySQL 初始化SQL
MYSQL_SCHEMA = """
-- 链信息表
CREATE TABLE IF NOT EXISTS chains (
    id INT PRIMARY KEY AUTO_INCREMENT,
    chain_id INT NOT NULL COMMENT '链ID',
    name VARCHAR(50) NOT NULL COMMENT '链名称',
    symbol VARCHAR(20) NOT NULL COMMENT '代币符号',
    rpc_urls JSON COMMENT 'RPC节点列表',
    explorer_url VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_chain_id (chain_id)
) ENGINE=InnoDB COMMENT='区块链信息表';

-- 代币信息表
CREATE TABLE IF NOT EXISTS tokens (
    id INT PRIMARY KEY AUTO_INCREMENT,
    chain_id INT NOT NULL,
    address VARCHAR(42) NOT NULL COMMENT '合约地址',
    symbol VARCHAR(20) NOT NULL,
    name VARCHAR(100),
    decimals INT DEFAULT 18,
    is_native BOOLEAN DEFAULT FALSE COMMENT '是否原生代币',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chain_id) REFERENCES chains(chain_id),
    UNIQUE KEY uk_chain_token (chain_id, address)
) ENGINE=InnoDB COMMENT='代币信息表';

-- 交易对信息表
CREATE TABLE IF NOT EXISTS trading_pairs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    symbol VARCHAR(50) NOT NULL COMMENT '交易对符号',
    base_asset VARCHAR(20) NOT NULL COMMENT '基础资产',
    quote_asset VARCHAR(20) NOT NULL COMMENT '计价资产',
    exchange VARCHAR(50) NOT NULL COMMENT '交易所',
    market_type VARCHAR(20) DEFAULT 'spot' COMMENT '市场类型',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_symbol_exchange (symbol, exchange)
) ENGINE=InnoDB COMMENT='交易对信息表';

-- 告警规则表
CREATE TABLE IF NOT EXISTS alert_rules (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    rule_type ENUM('price', 'volume', 'custom') NOT NULL,
    condition_config JSON NOT NULL COMMENT '条件配置JSON',
    severity ENUM('info', 'warning', 'critical') DEFAULT 'warning',
    is_active BOOLEAN DEFAULT TRUE,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT='告警规则表';

-- 告警记录表
CREATE TABLE IF NOT EXISTS alerts (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    rule_id INT NOT NULL,
    severity ENUM('info', 'warning', 'critical'),
    message TEXT,
    data JSON COMMENT '触发时的数据快照',
    status ENUM('active', 'acknowledged', 'resolved') DEFAULT 'active',
    acknowledged_by INT,
    acknowledged_at TIMESTAMP NULL,
    resolved_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rule_id) REFERENCES alert_rules(id),
    INDEX idx_created_at (created_at),
    INDEX idx_status (status)
) ENGINE=InnoDB COMMENT='告警记录表';

-- 系统配置表
CREATE TABLE IF NOT EXISTS system_configs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    config_key VARCHAR(100) NOT NULL UNIQUE,
    config_value TEXT,
    description VARCHAR(255),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT='系统配置表';

-- 插入默认链信息
INSERT INTO chains (chain_id, name, symbol, rpc_urls, explorer_url) VALUES
(1, 'Ethereum', 'ETH', '["https://eth-mainnet.g.alchemy.com"]', 'https://etherscan.io'),
(56, 'BSC', 'BNB', '["https://bsc-dataseed.binance.org"]', 'https://bscscan.com'),
(137, 'Polygon', 'MATIC', '["https://polygon-mainnet.g.alchemy.com"]', 'https://polygonscan.com'),
(42161, 'Arbitrum', 'ETH', '["https://arb-mainnet.g.alchemy.com"]', 'https://arbiscan.io'),
(8453, 'Base', 'ETH', '["https://base-mainnet.g.alchemy.com"]', 'https://basescan.org')
ON DUPLICATE KEY UPDATE updated_at = CURRENT_TIMESTAMP;
"""


async def init_mysql():
    """初始化MySQL数据库"""
    logger.info("initializing_mysql")

    try:
        conn = pymysql.connect(
            host=settings.mysql_host,
            port=settings.mysql_port,
            user=settings.mysql_user,
            password=settings.mysql_password,
            database=settings.mysql_database,
        )

        with conn.cursor() as cursor:
            # 执行SQL语句
            for statement in MYSQL_SCHEMA.split(';'):
                statement = statement.strip()
                if statement:
                    cursor.execute(statement)

        conn.commit()
        conn.close()

        logger.info("mysql_initialized_successfully")
        return True

    except Exception as e:
        logger.error("mysql_initialization_failed", error=str(e))
        return False


async def init_tdengine():
    """初始化TDengine数据库"""
    logger.info("initializing_tdengine")

    try:
        import taos

        conn = taos.connect(
            host=settings.tdengine_host,
            port=settings.tdengine_port,
            user=settings.tdengine_user,
            password=settings.tdengine_password,
        )

        cursor = conn.cursor()

        # 创建数据库
        cursor.execute(f"""
            CREATE DATABASE IF NOT EXISTS {settings.tdengine_database}
            KEEP 365 DAYS 10 BLOCKS 6
        """)

        # 使用数据库
        cursor.execute(f"USE {settings.tdengine_database}")

        # 创建K线超级表
        cursor.execute("""
            CREATE STABLE IF NOT EXISTS kline (
                ts TIMESTAMP,
                open DOUBLE,
                high DOUBLE,
                low DOUBLE,
                close DOUBLE,
                volume DOUBLE,
                amount DOUBLE,
                trade_count INT
            ) TAGS (
                symbol BINARY(50),
                interval BINARY(10),
                exchange BINARY(20),
                market_type BINARY(10)
            )
        """)

        # 创建tick数据超级表
        cursor.execute("""
            CREATE STABLE IF NOT EXISTS tick (
                ts TIMESTAMP,
                price DOUBLE,
                volume DOUBLE,
                side TINYINT
            ) TAGS (
                symbol BINARY(50),
                exchange BINARY(20),
                market_type BINARY(10)
            )
        """)

        # 创建技术指标超级表
        cursor.execute("""
            CREATE STABLE IF NOT EXISTS indicator (
                ts TIMESTAMP,
                sma_7 DOUBLE,
                sma_25 DOUBLE,
                sma_99 DOUBLE,
                ema_12 DOUBLE,
                ema_26 DOUBLE,
                rsi_14 DOUBLE,
                macd DOUBLE,
                macd_signal DOUBLE,
                macd_histogram DOUBLE
            ) TAGS (
                symbol BINARY(50),
                interval BINARY(10),
                exchange BINARY(20)
            )
        """)

        cursor.close()
        conn.close()

        logger.info("tdengine_initialized_successfully")
        return True

    except ImportError:
        logger.warning("taos_connector_not_installed_skipping_tdengine")
        return False
    except Exception as e:
        logger.error("tdengine_initialization_failed", error=str(e))
        return False


async def wait_for_services():
    """等待服务就绪"""
    logger.info("waiting_for_services")

    # 等待MySQL
    max_retries = 30
    for i in range(max_retries):
        try:
            conn = pymysql.connect(
                host=settings.mysql_host,
                port=settings.mysql_port,
                user=settings.mysql_user,
                password=settings.mysql_password,
            )
            conn.close()
            logger.info("mysql_is_ready")
            break
        except Exception:
            if i == max_retries - 1:
                logger.error("mysql_not_ready_after_retries")
                return False
            await asyncio.sleep(2)

    return True


async def main():
    """主函数"""
    logger.info("starting_database_initialization")

    # 等待服务就绪
    if not await wait_for_services():
        logger.error("services_not_ready_exit")
        sys.exit(1)

    # 初始化各个数据库
    results = {
        "mysql": await init_mysql(),
        "tdengine": await init_tdengine(),
    }

    logger.info("database_initialization_completed", results=results)

    if all(results.values()):
        logger.info("all_databases_initialized_successfully")
        sys.exit(0)
    else:
        logger.warning("some_databases_failed_to_initialize")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
