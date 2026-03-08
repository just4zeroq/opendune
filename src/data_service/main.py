"""
数据服务主入口
FastAPI应用
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.common.config import settings
from src.common.logger import configure_logging, get_logger
from src.data_service.api import market, trades, alerts, analytics

configure_logging(settings.log_level)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动
    logger.info("api_service_starting")
    yield
    # 关闭
    logger.info("api_service_stopping")


app = FastAPI(
    title="OpenDune API",
    description="实时加密数据分析平台 API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(market.router, prefix="/api/v1/market", tags=["market"])
app.include_router(trades.router, prefix="/api/v1/trades", tags=["trades"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["alerts"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "opendune-api"}


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "OpenDune API",
        "version": "1.0.0",
        "docs": "/docs",
    }
