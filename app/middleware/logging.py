import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger
from urllib.parse import unquote


class TrafficLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # 1. 处理请求
        response = await call_next(request)

        # 2. 计算耗时
        process_time = (time.time() - start_time) * 1000

        # 3. 构造日志内容
        # 排除不需要记录的路径（例如 health check 或 metrics）
        if request.url.path != "/health":
            parts = [
                request.client.host,
                request.method,
                str(response.status_code),
                f"{process_time:.2f}ms",
                request.url.path,
            ]
            if request.url.query:
                parts.append(str(unquote(request.url.query)))
            log_msg = " | ".join(parts)

            # 根据状态码决定日志级别
            if response.status_code >= 500:
                logger.error(log_msg)
            elif response.status_code >= 400:
                logger.warning(log_msg)
            else:
                logger.info(log_msg)

        return response
