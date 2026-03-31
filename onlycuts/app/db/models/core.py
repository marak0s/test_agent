from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from onlycuts.app.db.base import Base


class Channel(Base):
    __tablename__ = "channels"
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    language: Mapped[str] = mapped_column(String(16), nullable=False, default="en")
    locale: Mapped[str] = mapped_column(String(32), nullable=False, default="en_US")
    approver_telegram_user_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    approver_telegram_chat_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    publish_telegram_chat_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)


class Topic(Base):
    __tablename__ = "topics"
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    channel_id: Mapped[str] = mapped_column(ForeignKey("channels.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ContentItem(Base):
    __tablename__ = "content_items"
    __table_args__ = (UniqueConstraint("topic_id", "channel_id", name="uq_content_items_topic_channel"),)

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    channel_id: Mapped[str] = mapped_column(ForeignKey("channels.id"), nullable=False)
    topic_id: Mapped[str] = mapped_column(ForeignKey("topics.id"), nullable=False)
    goal: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    current_draft_id: Mapped[str | None] = mapped_column(UUID(as_uuid=True), nullable=True)


class Draft(Base):
    __tablename__ = "drafts"
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    content_item_id: Mapped[str] = mapped_column(ForeignKey("content_items.id"), nullable=False)
    channel_id: Mapped[str] = mapped_column(ForeignKey("channels.id"), nullable=False)
    body_text: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    review_status: Mapped[str] = mapped_column(String(32), nullable=False)


class Approval(Base):
    __tablename__ = "approvals"
    __table_args__ = (UniqueConstraint("source_type", "source_id", name="uq_approvals_source"),)

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    draft_id: Mapped[str] = mapped_column(ForeignKey("drafts.id"), nullable=False)
    actor_telegram_user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    source_type: Mapped[str] = mapped_column(String(32), nullable=False)
    source_id: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Publication(Base):
    __tablename__ = "publications"
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    draft_id: Mapped[str] = mapped_column(ForeignKey("drafts.id"), nullable=False)
    content_item_id: Mapped[str] = mapped_column(ForeignKey("content_items.id"), nullable=False)
    channel_id: Mapped[str] = mapped_column(ForeignKey("channels.id"), nullable=False)
    snapshot_text: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    telegram_chat_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    telegram_message_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    queued_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class JobRun(Base):
    __tablename__ = "jobs"
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    job_name: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Artifact(Base):
    __tablename__ = "artifacts"
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    kind: Mapped[str] = mapped_column(String(64), nullable=False)
    ref_id: Mapped[str] = mapped_column(String(128), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
