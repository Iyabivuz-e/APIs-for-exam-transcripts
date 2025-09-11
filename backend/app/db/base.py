"""
Database Base Module

This module contains the SQLAlchemy declarative base and common database utilities.
All database models should inherit from the Base class defined here.
"""

import uuid
from sqlalchemy import Column, DateTime, String
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.sql import func


@as_declarative()
class Base:
    """
    Base class for all database models.

    Provides common fields and functionality for all models:
    - Automatic table name generation from class name
    - Primary key UUID field
    - Created and updated timestamp fields
    """

    __name__: str
    __allow_unmapped__ = True  # Allow legacy annotations

    # Generate table name automatically from class name
    @declared_attr
    def __tablename__(cls) -> str:
        """
        Generate table name from class name.

        Returns:
            str: Table name in lowercase with underscores
        """
        # Convert CamelCase to snake_case
        import re

        name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", cls.__name__)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()

    # Common fields for all models - Using UUID instead of Integer
    id = Column(
        String(36), 
        primary_key=True, 
        index=True, 
        default=lambda: str(uuid.uuid4()),
        unique=True,
        nullable=False
    )
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        """
        String representation of the model.

        Returns:
            str: String representation
        """
        return f"<{self.__class__.__name__}(id={self.id})>"
