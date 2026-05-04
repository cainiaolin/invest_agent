"""API路由模块"""

from app.api.routes.analyze import router as analyze_router
from app.api.routes.screen import router as screen_router
from app.api.routes.backtest import router as backtest_router

__all__ = ["analyze_router", "screen_router", "backtest_router"]
