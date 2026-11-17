from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime
from typing import Optional

from app.db.models import IssuePriority, IssueStatus


class IssueCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    status: IssueStatus = IssueStatus.TO_DO
    priority: IssuePriority = IssuePriority.MEDIUM
    assignee_id: Optional[int] = None

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Issue title cannot be blank")
        return value


class IssueUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[IssueStatus] = None
    priority: Optional[IssuePriority] = None
    assignee_id: Optional[int] = None

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            value = value.strip()
            if not value:
                raise ValueError("Issue title cannot be blank")
        return value


class Issue(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: IssueStatus
    priority: IssuePriority
    created_at: datetime
    updated_at: datetime
    reporter_id: int
    assignee_id: Optional[int] = None
    project_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class CommentCreate(BaseModel):
    body: str = Field(min_length=1, max_length=5000)


class CommentRead(BaseModel):
    id: int
    body: str
    created_at: datetime
    author_id: int
    author_name: str