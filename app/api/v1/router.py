from fastapi import APIRouter

from app.api.v1.batch_calling import router as batch_calling_router
from app.api.v1.health import router as health_router
from app.api.v1.users import router as users_router

router = APIRouter(prefix="/api/v1")

router.include_router(health_router, tags=["health"])
router.include_router(users_router, tags=["users"])
router.include_router(batch_calling_router, tags=["batch-calling"])
