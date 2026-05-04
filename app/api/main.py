"""FastAPI应用 - Web API入口"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import logging

logger = logging.getLogger(__name__)

# 创建FastAPI应用实例
app = FastAPI(
    title="InvestAgent API",
    description="基于LangGraph+Tushare的多Agent投资智能体系API",
    version="0.3.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 导入路由（延迟导入避免循环依赖）
try:
    from app.api.routes import analyze, screen, backtest

    # 路由本身已有prefix，添加统一前缀
    app.include_router(analyze.router, prefix="/api/v1")
    app.include_router(screen.router, prefix="/api/v1")
    app.include_router(backtest.router, prefix="/api/v1")
except ImportError as e:
    logger.warning(f"路由模块导入失败: {e}，API功能可能受限")


@app.get("/", response_class=HTMLResponse)
async def root():
    """API根路径"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>InvestAgent API</title>
    </head>
    <body>
        <h1>InvestAgent API</h1>
        <p>基于LangGraph+Tushare的多Agent投资智能体系</p>
        <ul>
            <li><a href="/docs">API文档 (Swagger)</a></li>
            <li><a href="/redoc">API文档 (ReDoc)</a></li>
        </ul>
        <h2>可用端点</h2>
        <ul>
            <li>POST /api/v1/analyze - 分析股票</li>
            <li>POST /api/v1/screen - 智能选股</li>
            <li>POST /api/v1/backtest - 策略回测</li>
            <li>WS /ws/analyze - 实时分析推送</li>
        </ul>
    </body>
    </html>
    """


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "version": "0.3.0"}


@app.websocket("/ws/analyze")
async def analyze_websocket(websocket: WebSocket):
    """WebSocket端点 - 实时分析推送"""
    await websocket.accept()
    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_json()

            # 处理分析请求
            # ... 实际分析逻辑 ...

            # 发送进度更新
            await websocket.send_json({
                "type": "progress",
                "message": f"正在分析 {data.get('stock_code')}..."
            })

    except WebSocketDisconnect:
        logger.info("WebSocket连接已断开")
    except Exception as e:
        logger.error(f"WebSocket错误: {e}")
        await websocket.close()


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理"""
    logger.error(f"全局异常: {exc}")
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "detail": "内部服务器错误"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
