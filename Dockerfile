FROM python:3.13.9-alpine AS builder
LABEL authors="Trrrrw"

WORKDIR /app

RUN apk add --no-cache curl tzdata gcc musl-dev linux-headers
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

COPY pyproject.toml uv.lock /app/
COPY app /app/app/

RUN ~/.local/bin/uv sync --frozen

FROM python:3.13.9-alpine AS runtime
RUN apk add --no-cache curl tzdata
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

WORKDIR /app
COPY --from=builder /app /app

ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Shanghai

EXPOSE 8888
VOLUME ["/app/data"]

CMD ["/root/.local/bin/uv", "run", "/app/app/main.py"]
