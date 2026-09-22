from sqlalchemy.orm import Session

from notification_service.models.user import UserModel


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user: UserModel) -> UserModel:
        self.db.add(user)
        self.db.flush()
        self.db.refresh(user)
        return user

    def find_by_email(self, email: str) -> UserModel | None:
        return self.db.query(UserModel).filter(UserModel.email == email).first()

    def commit(self) -> None:
        """Commit the current transaction."""

        self.db.commit()

    def rollback(self) -> None:
        """Rollback the current transaction."""

        self.db.rollback()
