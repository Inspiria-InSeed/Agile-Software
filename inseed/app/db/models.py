from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Text
from sqlalchemy.orm import relationship, DeclarativeBase
from sqlalchemy.sql import func
import enum


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


class User(Base):
    """
    User model representing individuals who can access the Inseed system.
    Stores authentication and profile information.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    assigned_issues = relationship("Issue", foreign_keys="Issue.assignee_id", back_populates="assignee")
    reported_issues = relationship("Issue", foreign_keys="Issue.reporter_id", back_populates="reporter")
    comments = relationship("Comment", back_populates="author")
    created_projects = relationship("Project", back_populates="creator")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    key = Column(String(10), unique=True, index=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id"))

    creator = relationship("User", back_populates="created_projects")
    issues = relationship("Issue", back_populates="project")


class IssueStatus(str, enum.Enum):
    """Enumeration of standard issue statuses."""
    BACKLOG = "BACKLOG"
    TO_DO = "TO_DO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


class IssuePriority(str, enum.Enum):
    """Enumeration of issue priority levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Issue(Base):
    """
    Issue model representing tasks, bugs, or stories within a project.
    """
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String)
    status = Column(Enum(IssueStatus), default=IssueStatus.TO_DO, nullable=False)
    priority = Column(Enum(IssuePriority), default=IssuePriority.MEDIUM, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    reporter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assignee_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True, index=True)

    reporter = relationship("User", foreign_keys=[reporter_id], back_populates="reported_issues")
    assignee = relationship("User", foreign_keys=[assignee_id], back_populates="assigned_issues")
    project = relationship("Project", back_populates="issues")
    comments = relationship("Comment", back_populates="issue", cascade="all, delete-orphan")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    issue_id = Column(Integer, ForeignKey("issues.id", ondelete="CASCADE"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    issue = relationship("Issue", back_populates="comments")
    author = relationship("User", back_populates="comments")