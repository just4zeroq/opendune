"""
行情API路由
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from src.common.models import KlineInterval
from src.data_service.services.market_service import MarketService

router = APIRouter()
market_service = MarketService()


@router.get("/ticker/{symbol}")
async def get_ticker(symbol: str, exchange: Optional[str] = None):
    """
    获取最新行情

    Args:
        symbol: 交易对符号，如 BTCUSDT
        exchange: 交易所，可选
    """
    try:
        ticker = await market_service.get_ticker(symbol, exchange)
        if not ticker:
            raise HTTPException(status_code=404, detail="Ticker not found")
        return ticker
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tickers")
async def get_tickers(
    exchange: Optional[str] = None,
    symbols: Optional[str] = None
):
    """
    获取多个交易对的行情

    Args:
        exchange: 交易所
        symbols: 交易对列表，逗号分隔，如 BTCUSDT,ETHUSDT
    """
    symbol_list = symbols.split(",") if symbols else None
    try:
        return await market_service.get_tickers(exchange, symbol_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/klines/{symbol}")
async def get_klines(
    symbol: str,
    interval: KlineInterval = Query(KlineInterval.M1, description="K线周期"),
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = Query(100, ge=1, le=1000, description="返回条数"),
    exchange: Optional[str] = None,
):
    """
    获取K线数据

    Args:
        symbol: 交易对符号
        interval: K线周期 (1m, 5m, 15m, 1h, 4h, 1d)
        start_time: 开始时间
        end_time: 结束时间
        limit: 返回条数
        exchange: 交易所
    """
    try:
        return await market_service.get_klines(
            symbol=symbol,
            interval=interval,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
            exchange=exchange,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/depth/{symbol}")
async def get_order_book(
    symbol: str,
    limit: int = Query(20, ge=1, le=100, description="深度档位"),
    exchange: Optional[str] = None,
):
    """
    获取订单簿深度

    Args:
        symbol: 交易对符号
        limit: 深度档位
        exchange: 交易所
    """
    try:
        return await market_service.get_order_book(symbol, limit, exchange)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/exchanges")
async def get_exchanges():
    """获取支持的交易所列表"""
    return {
        "exchanges": [
            {"id": "binance", "name": "Binance"},
            {"id": "okx", "name": "OKX"},
            {"id": "bybit", "name": "Bybit"},
            {"id": "bitget", "name": "Bitget"},
        ]
    }


@router.get("/chains")
async def get_chains():
    """获取支持的链列表"""
    return {
        "chains": [
            {"id": "ethereum", "name": "Ethereum", "symbol": "ETH"},
            {"id": "bsc", "name": "BSC", "symbol": "BNB"},
            {"id": "polygon", "name": "Polygon", "symbol": "MATIC"},
            {"id": "arbitrum", "name": "Arbitrum", "symbol": "ETH"},
            {"id": "base", "name": "Base", "symbol": "ETH"},
        ]
    }
