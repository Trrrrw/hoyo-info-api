FROM ghcr.io/astral-sh/uv:python3.13-alpine AS runtime
LABEL authors="Trrrrw"

WORKDIR /src

COPY pyproject.toml uv.lock /src/
COPY app /src/app/

RUN uv sync --frozen

ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Shanghai

EXPOSE 8888
VOLUME ["/src/.temp/data"]

CMD ["uv", "run", "-m", "app.main"]
