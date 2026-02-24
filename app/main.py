import asyncio
from fastapi import FastAPI
from fastapi_mcp import FastApiMCP

from app.core.app import Application


async def main():
    app = Application()

    fastapi_app = FastAPI(title="HOYO-INFO-API")
    await app.set_fastapi_app(fastapi_app)

    fastapi_mcp = FastApiMCP(
        app.fastapi_app,
        name="Hoyo Info MCP",
        description="0.1.0",
        exclude_tags=["System"],
    )
    await app.set_fastapi_mcp(fastapi_mcp)

    await app.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
