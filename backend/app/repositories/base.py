"""Base repository primitives."""
from sqlalchemy.orm import Session


class BaseRepository:
    """Base repository wrapper around SQLAlchemy Session."""

    def __init__(self, db: Session):
        self.db = db

    def add(self, model) -> None:
        self.db.add(model)

    def flush(self) -> None:
        self.db.flush()

    def refresh(self, model) -> None:
        self.db.refresh(model)
