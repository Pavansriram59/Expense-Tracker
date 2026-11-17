"""Declarative Base and reusable model mixins for SQLAlchemy 2.0."""

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column
from sqlalchemy.types import TypeDecorator, CHAR


class GUID(TypeDecorator):
    """Platform-independent GUID/UUID type.

    Uses PostgreSQL's UUID type, otherwise uses CHAR(36) for SQLite / tests.
    """

    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect: Any) -> Any:
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value: Any, dialect: Any) -> Any:
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return str(value)
        return str(uuid.UUID(str(value)))

    def process_result_value(self, value: Any, dialect: Any) -> Any:
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(str(value))


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy declarative models."""

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Default table name is snake_cased class name."""
        return cls.__name__.lower()


class TimestampMixin:
    """Provides UTC created_at and updated_at timestamps."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class SoftDeleteMixin:
    """Provides soft-deletion capabilities for offline-first synchronization."""

    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class UUIDPrimaryKeyMixin:
    """Provides UUID primary key with client-side or server-side UUID generation."""

    id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        primary_key=True,
        default=uuid.uuid4,
    )
