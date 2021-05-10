from fastapi import APIRouter
from app.api.api_v1.robots import config, file, search

router = APIRouter()
router.include_router(config.router, prefix="/robots", tags=["robots"])
router.include_router(file.router, prefix="/robots", tags=["robots"])
router.include_router(search.router, prefix="/robots", tags=["robots"])
