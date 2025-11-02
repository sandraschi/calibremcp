"""
Base model for SQLAlchemy models.
"""

from typing import Any, Dict
from sqlalchemy.ext.declarative import declarative_base

# Create a base class for all models
Base = declarative_base()


class BaseMixin:
    """Mixin class that provides common functionality to all models."""

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model instance to a dictionary.

        Returns:
            Dictionary representation of the model
        """
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)

            # Convert datetime objects to ISO format strings
            if hasattr(value, "isoformat"):
                value = value.isoformat()

            result[column.name] = value

        return result

    def update(self, **kwargs: Any) -> None:
        """
        Update model attributes.

        Args:
            **kwargs: Attributes to update
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
