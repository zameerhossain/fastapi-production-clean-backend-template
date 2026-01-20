from fastapi import APIRouter

from src.controller.demo_controller import router as demo_user_router

routers = APIRouter(prefix="/api")

routers.include_router(demo_user_router)
