"""
Bybit 数据采集器
"""

import asyncio
from decimal import Decimal
from typing import Callable, List, Optional

import ccxt.async_support as ccxt

from src.common.config import settings
from src.common.logger import get_logger
from src.common.models import KlineEvent, KlineInterval, MarketType, TickerEvent, TradeEvent, TradeSide

logger = get_logger(__name__)


class BybitCollector:
    """Bybit 数据采集器"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        secret: Optional[str] = None,
        testnet: bool = False,
    ):
        self.api_key = api_key or settings.bybit_api_key
        self.secret = secret or settings.bybit_secret_key
        self.testnet = testnet or settings.bybit_testnet

        config = {
            'apiKey': self.api_key,
            'secret': self.secret,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot',
            }
        }

        self.exchange = ccxt.bybit(config)
        self.running = False
        self._tasks = []
        self.ticker_callbacks = []
        self.trade_callbacks = []
        self.kline_callbacks = []

        logger.info("bybit_collector_initialized", testnet=self.testnet)

    async def start(self):
        """启动采集器"""
        self.running = True
        logger.info("bybit_collector_started")

    async def stop(self):
        """停止采集器"""
        self.running = False
        for task in self._tasks:
            task.cancel()
        await self.exchange.close()
        logger.info("bybit_collector_stopped")

    def subscribe_ticker(self, callback: Callable[[TickerEvent], None]):
        """订阅行情"""
        self.ticker_callbacks.append(callback)

    def subscribe_trades(self, callback: Callable[[TradeEvent], None]):
        """订阅成交"""
        self.trade_callbacks.append(callback)

    def subscribe_klines(self, callback: Callable[[KlineEvent], None]):
        """订阅K线"""
        self.kline_callbacks.append(callback)

    async def subscribe_symbols(self, symbols: List[str]):
        """订阅交易对"""
        for symbol in symbols:
            task = asyncio.create_task(self._ticker_loop(symbol))
            self._tasks.append(task)
            task = asyncio.create_task(self._trades_loop(symbol))
            self._tasks.append(task)
            task = asyncio.create_task(self._klines_loop(symbol))
            self._tasks.append(task)

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
                await asyncio.sleep(1)
            except Exception as e:
                logger.error("bybit_ticker_error", symbol=symbol, error=str(e))
                await asyncio.sleep(5)

    async def _trades_loop(self, symbol: str):
        """成交数据循环"""
        while self.running:
            try:
                trades = await self.exchange.fetch_trades(symbol, limit=100)
                for trade in trades:
                    event = self._convert_trade(trade)
                    for callback in self.trade_callbacks:
                        try:
                            if asyncio.iscoroutinefunction(callback):
                                await callback(event)
                            else:
                                callback(event)
                        except Exception as e:
                            logger.error("trade_callback_error", error=str(e))
                await asyncio.sleep(1)
            except Exception as e:
                logger.error("bybit_trades_error", symbol=symbol, error=str(e))
                await asyncio.sleep(5)

    async def _klines_loop(self, symbol: str, interval: str = "1m"):
        """K线数据循环"""
        while self.running:
            try:
                ohlcv = await self.exchange.fetch_ohlcv(symbol, timeframe=interval, limit=100)
                for candle in ohlcv:
                    timestamp, open_p, high, low, close, volume = candle
                    event = KlineEvent(
                        symbol=symbol.replace("/", ""),
                        interval=KlineInterval.M1,
                        open=Decimal(str(open_p)),
                        high=Decimal(str(high)),
                        low=Decimal(str(low)),
                        close=Decimal(str(close)),
                        volume=Decimal(str(volume)),
                        timestamp=timestamp,
                        source="bybit",
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
                await asyncio.sleep(60)
            except Exception as e:
                logger.error("bybit_klines_error", symbol=symbol, error=str(e))
                await asyncio.sleep(5)

    def _convert_ticker(self, ticker: dict) -> TickerEvent:
        """转换行情数据"""
        return TickerEvent(
            symbol=ticker['symbol'].replace("/", ""),
            price=Decimal(str(ticker['last'])) if ticker['last'] else Decimal('0'),
            bid=Decimal(str(ticker['bid'])) if ticker['bid'] else None,
            ask=Decimal(str(ticker['ask'])) if ticker['ask'] else None,
            timestamp=ticker['timestamp'],
            source="bybit",
            market_type=MarketType.SPOT,
        )

    def _convert_trade(self, trade: dict) -> TradeEvent:
        """转换成交数据"""
        return TradeEvent(
            symbol=trade['symbol'].replace("/", ""),
            price=Decimal(str(trade['price'])),
            quantity=Decimal(str(trade['amount'])),
            side=TradeSide.BUY if trade['side'] == 'buy' else TradeSide.SELL,
            timestamp=trade['timestamp'],
            source="bybit",
            trade_id=str(trade['id']),
            market_type=MarketType.SPOT,
        )
