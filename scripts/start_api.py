"""
API服务启动脚本
"""

import uvicorn
from src.common.config import settings
from src.common.logger import configure_logging

configure_logging(settings.log_level)

if __name__ == "__main__":
    uvicorn.run(
        "src.data_service.main:app",
        host=settings.api_host,
        port=settings.api_port,
        workers=settings.api_workers,
        reload=settings.debug,
    )
