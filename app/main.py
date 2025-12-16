import time
import uvicorn
import threading
from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
from fastapi.responses import RedirectResponse
from loguru import logger

from core.config import setup_logger, settings
from middleware.logging import TrafficLogMiddleware
from api import api_router

app = FastAPI()
SERVER = None


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok"}


def start_app():
    if settings.DEBUG:
        app.add_middleware(TrafficLogMiddleware)
    app.include_router(api_router)

    mcp = FastApiMCP(app)
    mcp.mount_http()
    mcp.mount_sse()

    host = settings.HOST
    port = settings.PORT
    config = uvicorn.Config(
        app=app,
        host=host,
        port=port,
        reload=False,
        workers=1,
        log_config=None,
    )
    SERVER = uvicorn.Server(config=config)
    threading.Thread(target=SERVER.run, daemon=True).start()

    display_host = host if host not in ["0.0.0.0", "127.0.0.1"] else "127.0.0.1"
    logger.info(f"服务器已启动，监听地址 http://{display_host}:{port}")


def stop_app():
    logger.info("正在关闭...")
    if SERVER:
        SERVER.should_exit = True
    logger.info("已退出")


if __name__ == "__main__":
    setup_logger()

    start_app()
    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        stop_app()
