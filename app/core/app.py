import asyncio
import threading
from uvicorn import Config, Server
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi_mcp import FastApiMCP

from app.middleware.logging import TrafficLogMiddleware
from app.core.config import app_config
from app.utils.logger import get_logger
from app.api import api_router


class Application:
    logger = get_logger("APP")
    fastapi_app: FastAPI | None = None
    fastapi_mcp: FastApiMCP | None = None
    uvicorn_server: Server | None = None

    def __init__(self) -> None:
        pass

    async def set_fastapi_app(self, fastapi_app: FastAPI) -> None:
        self.fastapi_app = fastapi_app

        @self.fastapi_app.get("/", include_in_schema=False)
        async def root():
            return RedirectResponse(url="/docs")

        @self.fastapi_app.get("/health", tags=["System"])
        async def health_check():
            return {"status": "ok"}

        self.fastapi_app.add_middleware(TrafficLogMiddleware)
        self.fastapi_app.include_router(api_router)

    async def set_fastapi_mcp(self, fastapi_mcp: FastApiMCP) -> None:
        self.fastapi_mcp = fastapi_mcp
        self.fastapi_mcp.mount_http()
        self.fastapi_mcp.mount_sse()

    async def run(self) -> None:
        host = app_config.host
        port = app_config.port
        config = Config(
            app=self.fastapi_app,
            host=host,
            port=port,
            reload=False,
            workers=1,
            log_config=None,
        )
        self.uvicorn_server = Server(config=config)
        threading.Thread(target=self.uvicorn_server.run, daemon=True).start()

        display_host = host if host not in ["0.0.0.0", "127.0.0.1"] else "127.0.0.1"
        self.logger.info(f"服务器已启动，监听地址 http://{display_host}:{port}")

        try:
            while True:
                await asyncio.sleep(1)
        except (KeyboardInterrupt, asyncio.CancelledError):
            self.logger.opt(raw=True).info("\n")
            self.logger.info("正在关闭...")
        finally:
            self._cleanup()

    def _cleanup(self) -> None:
        if self.uvicorn_server:
            self.uvicorn_server.should_exit = True
        self.logger.info("应用已停止")
