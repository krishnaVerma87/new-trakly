"""Workflow template and column models for customizable Kanban boards."""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.db.base import BaseModel


class WorkflowTemplate(BaseModel):
    """
    Workflow template defining a set of Kanban columns.
    Templates are organization-scoped and can be reused across projects.
    """
    __tablename__ = "workflow_templates"

    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_default = Column(Boolean, default=False, nullable=False)
    is_system = Column(Boolean, default=False, nullable=False)  # System templates can't be deleted
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="workflow_templates")
    columns = relationship(
        "WorkflowColumn",
        back_populates="template",
        cascade="all, delete-orphan",
        order_by="WorkflowColumn.position"
    )
    projects = relationship("Project", back_populates="workflow_template")
    creator = relationship("User", foreign_keys=[created_by])


class WorkflowColumn(BaseModel):
    """
    Individual column within a workflow template.
    Defines the status/stage in the Kanban flow.
    """
    __tablename__ = "workflow_columns"

    template_id = Column(String(36), ForeignKey("workflow_templates.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(50), nullable=False)
    position = Column(Integer, nullable=False)  # Order in the workflow
    wip_limit = Column(Integer, nullable=True)  # Work In Progress limit (null = no limit)
    color = Column(String(20), nullable=True)  # Hex color or named color for UI
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    template = relationship("WorkflowTemplate", back_populates="columns")
    issues = relationship("Issue", back_populates="workflow_column")
