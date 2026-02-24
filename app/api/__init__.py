import importlib
import pkgutil
from fastapi import APIRouter

api_router = APIRouter()

for loader, module_name, is_pkg in pkgutil.walk_packages(__path__):
    module = importlib.import_module(f".{module_name}.router", package=__package__)

    if hasattr(module, "router"):
        api_router.include_router(module.router, prefix=f"/{module_name}")
