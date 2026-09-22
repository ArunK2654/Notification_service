from fastapi import APIRouter, status

from notification_service.database import SessionLocal
from notification_service.redis import redis_client
from notification_service.services.health_service import HealthService
from notification_service.services.redis_service import RedisService

health_router = APIRouter(prefix="/health", tags=["health"])


@health_router.get("/", status_code=status.HTTP_200_OK)
def health() -> dict[str, str]:
    db = SessionLocal()

    try:
        redis_service = RedisService(redis_client)
        health_service = HealthService(
            db=db,
            redis_service=redis_service,
        )

        if health_service.check_health():
            return {"status": "ok"}

        return {"status": "unhealthy"}

    finally:
        db.close()
