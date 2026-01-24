"""Base model class with common fields and utilities."""
import re
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, String
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """SQLAlchemy declarative base class."""
    pass


class BaseModel(Base):
    """
    Abstract base model with common fields.

    Provides:
    - UUID primary key
    - Automatic table name generation from class name
    - Created/updated timestamps
    """

    __abstract__ = True

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    @declared_attr
    def __tablename__(cls) -> str:
        """
        Auto-generate table name from class name.

        Converts CamelCase to snake_case and pluralizes.
        Example: UserRole -> user_roles
        """
        name = cls.__name__
        # Convert CamelCase to snake_case
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        snake_case = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
        # Simple pluralization (add 's' or 'es')
        if snake_case.endswith("s") or snake_case.endswith("x"):
            return snake_case + "es"
        elif snake_case.endswith("y"):
            return snake_case[:-1] + "ies"
        return snake_case + "s"

    def to_dict(self) -> dict[str, Any]:
        """Convert model instance to dictionary."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
