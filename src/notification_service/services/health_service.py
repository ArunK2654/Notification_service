from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from notification_service.services.redis_service import RedisService


class HealthService:
    def __init__(
        self,
        db: Session,
        redis_service: RedisService,
    ):
        self.db = db
        self.redis_service = redis_service

    def check_database(self) -> bool:
        try:
            self.db.execute(text("SELECT 1"))
            return True
        except SQLAlchemyError:
            return False

    def check_redis(self) -> bool:
        return self.redis_service.ping()

    def check_health(self) -> bool:
        return self.check_database() and self.check_redis()
