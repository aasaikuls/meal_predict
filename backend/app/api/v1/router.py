from fastapi import APIRouter
from app.api.v1.routes import flights, sessions, metrics, prediction

router = APIRouter()

router.include_router(flights.router, tags=["flights"])
router.include_router(sessions.router, tags=["sessions"])
router.include_router(metrics.router, tags=["metrics"])
router.include_router(prediction.router, tags=["prediction"])
