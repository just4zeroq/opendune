"""
TDengine 客户端
"""

from typing import Any, Dict, List, Optional

from src.common.logger import get_logger

logger = get_logger(__name__)


class TDengineClient:
    """TDengine时序数据库客户端"""

    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        database: str,
    ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self._conn = None

    def connect(self):
        """连接数据库"""
        try:
            import taos
            self._conn = taos.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
            )
            logger.info("tdengine_connected", host=self.host, database=self.database)
        except ImportError:
            logger.warning("taos_connector_not_installed")
        except Exception as e:
            logger.error("tdengine_connection_failed", error=str(e))
            raise

    def close(self):
        """关闭连接"""
        if self._conn:
            self._conn.close()
            logger.info("tdengine_disconnected")

    def execute(self, sql: str) -> int:
        """执行SQL"""
        if not self._conn:
            self.connect()

        try:
            return self._conn.execute(sql)
        except Exception as e:
            logger.error("tdengine_execute_error", sql=sql, error=str(e))
            raise

    def query(self, sql: str) -> List[Dict[str, Any]]:
        """查询数据"""
        if not self._conn:
            self.connect()

        try:
            cursor = self._conn.cursor()
            cursor.execute(sql)
            columns = [desc[0] for desc in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            cursor.close()
            return results
        except Exception as e:
            logger.error("tdengine_query_error", sql=sql, error=str(e))
            return []

    def insert_kline(
        self,
        symbol: str,
        interval: str,
        exchange: str,
        data: Dict[str, Any],
    ):
        """插入K线数据"""
        try:
            table_name = f"kline_{interval}_{symbol}_{exchange}"
            sql = f"""
                INSERT INTO {table_name} USING kline TAGS ('{symbol}', '{interval}', '{exchange}', 'spot')
                VALUES ({data['ts']}, {data['open']}, {data['high']}, {data['low']}, {data['close']}, {data['volume']}, {data.get('amount', 0)}, {data.get('trade_count', 0)})
            """
            self.execute(sql)
        except Exception as e:
            logger.error("insert_kline_error", symbol=symbol, error=str(e))

    def insert_tick(self, symbol: str, exchange: str, data: Dict[str, Any]):
        """插入Tick数据"""
        try:
            table_name = f"tick_{symbol}_{exchange}"
            sql = f"""
                INSERT INTO {table_name} USING tick TAGS ('{symbol}', '{exchange}', 'spot')
                VALUES ({data['ts']}, {data['price']}, {data['volume']}, {data['side']})
            """
            self.execute(sql)
        except Exception as e:
            logger.error("insert_tick_error", symbol=symbol, error=str(e))
