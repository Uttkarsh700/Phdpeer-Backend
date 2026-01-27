"""Base service class with common database operations."""
from typing import Generic, TypeVar, Type, Optional, List, Any
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from app.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseService(Generic[ModelType]):
    """
    Base service with CRUD operations.
    
    Provides common database operations for any model.
    
    Args:
        model: SQLAlchemy model class
        db: Database session
    
    Example:
        class UserService(BaseService[User]):
            pass
            
        user_service = UserService(User, db)
        user = user_service.get(user_id=1)
    """
    
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db
    
    def get(self, id: Any) -> Optional[ModelType]:
        """Get a single record by ID."""
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_multi(
        self, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[ModelType]:
        """Get multiple records with pagination."""
        return self.db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, obj_in: dict) -> ModelType:
        """Create a new record."""
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def update(self, id: Any, obj_in: dict) -> Optional[ModelType]:
        """Update an existing record."""
        db_obj = self.get(id)
        if db_obj:
            obj_data = jsonable_encoder(db_obj)
            update_data = obj_in if isinstance(obj_in, dict) else obj_in.dict(exclude_unset=True)
            for field in obj_data:
                if field in update_data:
                    setattr(db_obj, field, update_data[field])
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
        return db_obj
    
    def delete(self, id: Any) -> Optional[ModelType]:
        """Delete a record."""
        db_obj = self.get(id)
        if db_obj:
            self.db.delete(db_obj)
            self.db.commit()
        return db_obj
