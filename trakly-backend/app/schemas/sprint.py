"""Sprint schemas for request/response validation."""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class SprintBase(BaseModel):
    """Base sprint schema."""
    name: str = Field(..., min_length=1, max_length=255)
    goal: Optional[str] = None
    start_date: date
    end_date: date
    is_active: bool = False


class SprintCreate(SprintBase):
    """Schema for creating a sprint."""
    project_id: str


class SprintUpdate(BaseModel):
    """Schema for updating a sprint."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    goal: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: Optional[bool] = None
    is_completed: Optional[bool] = None


class SprintResponse(BaseModel):
    """Schema for sprint response."""
    id: str
    project_id: str
    name: str
    goal: Optional[str] = None
    start_date: date
    end_date: date
    sprint_number: int
    is_active: bool
    is_completed: bool
    status: str  # computed: 'planned', 'active', 'completed'
    issue_count: int = 0
    completed_issue_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

    @staticmethod
    def from_orm_with_counts(sprint, issue_count: int = 0, completed_issue_count: int = 0):
        """Create response with computed fields."""
        # Determine status
        if sprint.is_completed:
            status = 'completed'
        elif sprint.is_active:
            status = 'active'
        else:
            status = 'planned'

        data = {
            'id': sprint.id,
            'project_id': sprint.project_id,
            'name': sprint.name,
            'goal': sprint.goal,
            'start_date': sprint.start_date,
            'end_date': sprint.end_date,
            'sprint_number': sprint.sprint_number,
            'is_active': sprint.is_active,
            'is_completed': sprint.is_completed,
            'status': status,
            'issue_count': issue_count,
            'completed_issue_count': completed_issue_count,
            'created_at': sprint.created_at,
            'updated_at': sprint.updated_at,
        }
        return SprintResponse(**data)


class SprintCompletion(BaseModel):
    """Schema for completing a sprint."""
    move_issues_to: str  # 'backlog' or 'new_sprint_id'
    new_sprint_id: Optional[str] = None


class SprintStats(BaseModel):
    """Schema for sprint statistics."""
    total_issues: int
    completed_issues: int
    incomplete_issues: int
    by_status: dict[str, int]
    by_priority: dict[str, int]
    by_assignee: dict[str, int]
