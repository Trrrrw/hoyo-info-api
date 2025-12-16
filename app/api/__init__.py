from fastapi import APIRouter
from .hoyo_video.router import router as hoyo_router

api_router = APIRouter()

api_router.include_router(hoyo_router, prefix="/hoyo_video")
