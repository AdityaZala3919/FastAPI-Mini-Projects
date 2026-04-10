from uuid import UUID
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import (
    String,
    Integer,
    DateTime,
    Float,
    ForeignKey,
    Text,
    Index,
)

from database import Base

class Prompts(Base):
    __tablename__ = "prompts"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), index=True, nullable=False)
    unique_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())

    __table_args__ = (Index("ix_prompts_id_version", "id", "version"),)

class Agents(Base):
    __tablename__ = "agents"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, index=True)
    prompt_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    model_name: Mapped[str] = mapped_column(String, nullable=False)
    temperature: Mapped[float] = mapped_column(Float, default=0.7)
    max_output_tokens: Mapped[int] = mapped_column(Integer, default=8192)