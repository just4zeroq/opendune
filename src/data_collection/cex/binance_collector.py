"""
币安数据采集器
"""

import asyncio
from decimal import Decimal
from typing import Callable, Dict, List, Optional, Set

import ccxt.async_support as ccxt

from src.common.config import settings
from src.common.exceptions import ExchangeAPIError
from src.common.logger import get_logger
from src.common.models import KlineEvent, KlineInterval, MarketType, OrderBookEvent, TickerEvent, TradeEvent, TradeSide

logger = get_logger(__name__)


class BinanceCollector:
    """
    币安数据采集器

    支持功能：
    - 实时行情(Ticker)
    - 成交数据(Trades)
    - K线数据(Klines)
    - 订单簿(OrderBook)
    - 通过WebSocket的实时推送
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        secret: Optional[str] = None,
        testnet: bool = False,
    ):
        self.api_key = api_key or settings.binance_api_key
        self.secret = secret or settings.binance_secret_key
        self.testnet = testnet or settings.binance_testnet

        # 初始化CCXT交易所实例
        config = {
            'apiKey': self.api_key,
            'secret': self.secret,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot',
                'adjustForTimeDifference': True,
            }
        }

        if self.testnet:
            config['urls'] = {
                'api': {
                    'public': 'https://testnet.binance.vision/api',
                    'private': 'https://testnet.binance.vision/api',
                }
            }

        self.exchange = ccxt.binance(config)

        # 订阅管理
        self.subscribed_symbols: Set[str] = set()
        self.running = False
        self._tasks: List[asyncio.Task] = []

        # 回调函数
        self.ticker_callbacks: List[Callable[[TickerEvent], None]] = []
        self.trade_callbacks: List[Callable[[TradeEvent], None]] = []
        self.kline_callbacks: List[Callable[[KlineEvent], None]] = []
        self.orderbook_callbacks: List[Callable[[OrderBookEvent], None]] = []

        logger.info(
            "binance_collector_initialized",
            testnet=self.testnet,
            has_api_key=bool(self.api_key),
        )

    async def start(self):
        """启动采集器"""
        if self.running:
            return

        self.running = True
        logger.info("binance_collector_started")

    async def stop(self):
        """停止采集器"""
        self.running = False

        # 取消所有任务
        for task in self._tasks:
            task.cancel()

        # 关闭交易所连接
        await self.exchange.close()

        self._tasks.clear()
        logger.info("binance_collector_stopped")

    def subscribe_ticker(self, callback: Callable[[TickerEvent], None]):
        """订阅行情"""
        self.ticker_callbacks.append(callback)

    def subscribe_trades(self, callback: Callable[[TradeEvent], None]):
        """订阅成交"""
        self.trade_callbacks.append(callback)

    def subscribe_klines(self, callback: Callable[[KlineEvent], None]):
        """订阅K线"""
        self.kline_callbacks.append(callback)

    def subscribe_orderbook(self, callback: Callable[[OrderBookEvent], None]):
        """订阅订单簿"""
        self.orderbook_callbacks.append(callback)

    async def subscribe_symbols(self, symbols: List[str]):
        """
        订阅交易对

        Args:
            symbols: 交易对列表，如 ["BTC/USDT", "ETH/USDT"]
        """
        self.subscribed_symbols.update(symbols)

        # 启动各个数据流的采集任务
        for symbol in symbols:
            # 行情数据
            task = asyncio.create_task(self._ticker_loop(symbol))
            self._tasks.append(task)

            # 成交数据
            task = asyncio.create_task(self._trades_loop(symbol))
            self._tasks.append(task)

            # K线数据
            task = asyncio.create_task(self._klines_loop(symbol))
            self._tasks.append(task)

            # 订单簿
            task = asyncio.create_task(self._orderbook_loop(symbol))
            self._tasks.append(task)

        logger.info("binance_subscribed_symbols", symbols=symbols)

    async def _ticker_loop(self, symbol: str):
        """行情数据循环"""
        while self.running:
            try:
                ticker = await self.exchange.fetch_ticker(symbol)
                event = self._convert_ticker(ticker)

                for callback in self.ticker_callbacks:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(event)
                        else:
                            callback(event)
                    except Exception as e:
                        logger.error("ticker_callback_error", error=str(e))

                await asyncio.sleep(1)  # 1秒间隔

            except Exception as e:
                logger.error("binance_ticker_error", symbol=symbol, error=str(e))
                await asyncio.sleep(5)

    async def _trades_loop(self, symbol: str):
        """成交数据循环"""
        last_trade_id = None

        while self.running:
            try:
                params = {}
                if last_trade_id:
                    params['since'] = last_trade_id

                trades = await self.exchange.fetch_trades(symbol, limit=100, params=params)

                for trade in trades:
                    if last_trade_id and trade['id'] <= last_trade_id:
                        continue

                    event = self._convert_trade(trade)

                    for callback in self.trade_callbacks:
                        try:
                            if asyncio.iscoroutinefunction(callback):
                                await callback(event)
                            else:
                                callback(event)
                        except Exception as e:
                            logger.error("trade_callback_error", error=str(e))

                    last_trade_id = trade['id']

                await asyncio.sleep(1)

            except Exception as e:
                logger.error("binance_trades_error", symbol=symbol, error=str(e))
                await asyncio.sleep(5)

    async def _klines_loop(self, symbol: str, interval: str = "1m"):
        """K线数据循环"""
        last_timestamp = None

        while self.running:
            try:
                since = None
                if last_timestamp:
                    since = last_timestamp + 1

                ohlcv = await self.exchange.fetch_ohlcv(
                    symbol,
                    timeframe=interval,
                    since=since,
                    limit=100
                )

                for candle in ohlcv:
                    timestamp, open_p, high, low, close, volume = candle

                    if last_timestamp and timestamp <= last_timestamp:
                        continue

                    event = KlineEvent(
                        symbol=symbol.replace("/", ""),
                        interval=KlineInterval.M1 if interval == "1m" else KlineInterval(interval),
                        open=Decimal(str(open_p)),
                        high=Decimal(str(high)),
                        low=Decimal(str(low)),
                        close=Decimal(str(close)),
                        volume=Decimal(str(volume)),
                        timestamp=timestamp,
                        source="binance",
                        market_type=MarketType.SPOT,
                    )

                    for callback in self.kline_callbacks:
                        try:
                            if asyncio.iscoroutinefunction(callback):
                                await callback(event)
                            else:
                                callback(event)
                        except Exception as e:
                            logger.error("kline_callback_error", error=str(e))

                    last_timestamp = timestamp

                await asyncio.sleep(60)  # K线每分钟更新

            except Exception as e:
                logger.error("binance_klines_error", symbol=symbol, error=str(e))
                await asyncio.sleep(5)

    async def _orderbook_loop(self, symbol: str):
        """订单簿循环"""
        while self.running:
            try:
                orderbook = await self.exchange.fetch_order_book(symbol, limit=20)

                from src.common.models import OrderBookLevel

                bids = [OrderBookLevel(price=Decimal(str(b[0])), volume=Decimal(str(b[1]))) for b in orderbook['bids'][:10]]
                asks = [OrderBookLevel(price=Decimal(str(a[0])), volume=Decimal(str(a[1]))) for a in orderbook['asks'][:10]]

                event = OrderBookEvent(
                    symbol=symbol.replace("/", ""),
                    bids=bids,
                    asks=asks,
                    timestamp=orderbook['timestamp'],
                    source="binance",
                    market_type=MarketType.SPOT,
                )

                for callback in self.orderbook_callbacks:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(event)
                        else:
                            callback(event)
                    except Exception as e:
                        logger.error("orderbook_callback_error", error=str(e))

                await asyncio.sleep(1)

            except Exception as e:
                logger.error("binance_orderbook_error", symbol=symbol, error=str(e))
                await asyncio.sleep(5)

    def _convert_ticker(self, ticker: Dict) -> TickerEvent:
        """转换行情数据"""
        return TickerEvent(
            symbol=ticker['symbol'].replace("/", ""),
            price=Decimal(str(ticker['last'])) if ticker['last'] else Decimal('0'),
            bid=Decimal(str(ticker['bid'])) if ticker['bid'] else None,
            ask=Decimal(str(ticker['ask'])) if ticker['ask'] else None,
            bid_volume=Decimal(str(ticker['bidVolume'])) if ticker['bidVolume'] else None,
            ask_volume=Decimal(str(ticker['askVolume'])) if ticker['askVolume'] else None,
            volume_24h=Decimal(str(ticker['quoteVolume'])) if ticker['quoteVolume'] else None,
            change_24h=Decimal(str(ticker['change'])) if ticker['change'] else None,
            change_24h_percent=Decimal(str(ticker['percentage'])) if ticker['percentage'] else None,
            timestamp=ticker['timestamp'],
            source="binance",
            market_type=MarketType.SPOT,
        )

    def _convert_trade(self, trade: Dict) -> TradeEvent:
        """转换成交数据"""
        return TradeEvent(
            symbol=trade['symbol'].replace("/", ""),
            price=Decimal(str(trade['price'])),
            quantity=Decimal(str(trade['amount'])),
            side=TradeSide.BUY if trade['side'] == 'buy' else TradeSide.SELL,
            timestamp=trade['timestamp'],
            source="binance",
            trade_id=str(trade['id']),
            market_type=MarketType.SPOT,
        )

    async def fetch_ohlcv(
        self,
        symbol: str,
        interval: str = "1m",
        since: Optional[int] = None,
        limit: int = 100
    ) -> List[List]:
        """获取历史K线数据"""
        try:
            return await self.exchange.fetch_ohlcv(symbol, interval, since, limit)
        except Exception as e:
            logger.error("binance_fetch_ohlcv_error", symbol=symbol, error=str(e))
            raise ExchangeAPIError("binance", 500, str(e))

    async def fetch_tickers(self, symbols: Optional[List[str]] = None) -> Dict:
        """获取多个交易对的行情"""
        try:
            return await self.exchange.fetch_tickers(symbols)
        except Exception as e:
            logger.error("binance_fetch_tickers_error", error=str(e))
            raise ExchangeAPIError("binance", 500, str(e))
