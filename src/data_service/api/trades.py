"""
交易API路由
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from src.common.models import DataSource
from src.data_service.services.trade_service import TradeService

router = APIRouter()
trade_service = TradeService()


@router.get("/recent")
async def get_recent_trades(
    symbol: Optional[str] = None,
    source: Optional[DataSource] = None,
    limit: int = Query(100, ge=1, le=1000),
):
    """获取最近成交"""
    try:
        return await trade_service.get_recent_trades(
            symbol=symbol,
            source=source,
            limit=limit,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/{symbol}")
async def get_trade_stats(
    symbol: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
):
    """获取交易统计"""
    try:
        return await trade_service.get_trade_stats(
            symbol=symbol,
            start_time=start_time,
            end_time=end_time,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/volume/{symbol}")
async def get_volume_analysis(
    symbol: str,
    interval: str = Query("1h", regex="^(1h|4h|1d)$"),
    limit: int = Query(24, ge=1, le=168),
):
    """获取成交量分析"""
    try:
        return await trade_service.get_volume_analysis(
            symbol=symbol,
            interval=interval,
            limit=limit,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
