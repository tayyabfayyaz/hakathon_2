from fastapi import APIRouter

from src.api.v1.auth import router as auth_router
from src.api.v1.todos import router as todos_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(todos_router)
