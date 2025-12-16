# HOYO-INFO-API

A FastAPI-based backend service for the [hoyo_video](https://github.com/Trrrrw/hoyo_video) and [hoyo_calendar](https://github.com/Trrrrw/hoyo_calendar) project.

## Project Structure

```
.
├── app
│   ├── api
│   │   ├── hoyo_video
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   └── services.py
│   │   └── __init__.py
│   ├── core
│   │   └── config.py
│   ├── middleware
│   │   ├── __init__.py
│   │   └── logging.py
│   ├── __init__.py
│   └── main.py
├── Dockerfile
├── README.md
├── pyproject.toml
├── requirements.txt
└── uv.lock
```

## Requirements

- Python >= 3.13.9
- Dependencies listed in `pyproject.toml`

## Installation

Using `uv` package manager:

```bash
uv sync
```

## Running the Application

```bash
uv run app/main.py
```

The API will be available at `http://localhost:8888`

## Docker

Build and run with Docker:

```bash
docker build -t hoyo-info-api:latest .
docker run -p 8888:8888 -v /host_dir:/app/data ghcr.io/trrrrw/hoyo-info-api:latest
```

## Features

- FastAPI framework
- Async file operations with `aiofiles`
- Structured logging with `loguru`
- Configuration management with Pydantic Settings
- ASGI server with Uvicorn
