import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    auth_provider: Mapped[str | None] = mapped_column(String(64), nullable=True)
    auth_provider_user_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True, unique=True
    )
    email: Mapped[str | None] = mapped_column(String(320), nullable=True, unique=True)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    workspace_memberships = relationship(
        "WorkspaceMember", back_populates="user", cascade="all, delete-orphan"
    )
