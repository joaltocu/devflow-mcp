"""Database models for DevFlow MCP Server."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all models."""

    pass


class Project(Base):
    """Project model - represents a software project."""

    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    path: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[Optional[str]] = mapped_column(String(50))
    framework: Mapped[Optional[str]] = mapped_column(String(50))
    repository_url: Mapped[Optional[str]] = mapped_column(Text)
    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    reviews: Mapped[List["Review"]] = relationship(back_populates="project")
    decisions: Mapped[List["Decision"]] = relationship(back_populates="project")
    interactions: Mapped[List["AgentInteraction"]] = relationship(
        back_populates="project"
    )


class Review(Base):
    """Review model - represents a code review."""

    __tablename__ = "reviews"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id"), nullable=False
    )
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    diff: Mapped[str] = mapped_column(Text, nullable=False)
    context: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    agent_type: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    # Relationships
    project: Mapped["Project"] = relationship(back_populates="reviews")
    issues: Mapped[List["ReviewIssue"]] = relationship(back_populates="review")


class ReviewIssue(Base):
    """Review issue model - represents an issue found in a review."""

    __tablename__ = "review_issues"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    review_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("reviews.id"), nullable=False
    )
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100))
    file_path: Mapped[Optional[str]] = mapped_column(Text)
    line_number: Mapped[Optional[int]] = mapped_column(Integer)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    suggestion: Mapped[Optional[str]] = mapped_column(Text)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    # Relationships
    review: Mapped["Review"] = relationship(back_populates="issues")


class Pattern(Base):
    """Pattern model - represents a learned pattern."""

    __tablename__ = "patterns"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    pattern_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    code_example: Mapped[Optional[str]] = mapped_column(Text)
    effectiveness_score: Mapped[float] = mapped_column(Float, default=0.0)
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    projects: Mapped[Optional[List[str]]] = mapped_column(JSONB)
    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class Decision(Base):
    """Decision model - represents an Architecture Decision Record (ADR)."""

    __tablename__ = "decisions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[Optional[str]] = mapped_column(String(50))
    context: Mapped[Optional[str]] = mapped_column(Text)
    decision: Mapped[str] = mapped_column(Text, nullable=False)
    consequences: Mapped[Optional[str]] = mapped_column(Text)
    alternatives: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSONB)
    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    project: Mapped["Project"] = relationship(back_populates="decisions")


class AgentInteraction(Base):
    """Agent interaction model - logs all agent tool calls."""

    __tablename__ = "agent_interactions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("projects.id")
    )
    agent_type: Mapped[str] = mapped_column(String(100), nullable=False)
    tool_name: Mapped[str] = mapped_column(String(255), nullable=False)
    input_params: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    output_result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    success: Mapped[Optional[bool]] = mapped_column(Boolean)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    # Relationships
    project: Mapped[Optional["Project"]] = relationship(
        back_populates="interactions"
    )


class KnowledgeBase(Base):
    """Knowledge base model - stores accumulated knowledge."""

    __tablename__ = "knowledge_base"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    topic: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[Optional[str]] = mapped_column(String(255))
    relevance_score: Mapped[float] = mapped_column(Float, default=0.0)
    tags: Mapped[Optional[List[str]]] = mapped_column(JSONB)
    projects: Mapped[Optional[List[str]]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
