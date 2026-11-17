from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.models import Issue, Project
from app.schemas.issue import IssueCreate, IssueUpdate


def get_issue(db: Session, issue_id: int) -> Optional[Issue]:
    """
    Retrieve a single issue by its ID.
    """
    return db.query(Issue).filter(Issue.id == issue_id).first()


def get_issues(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    project_id: Optional[int] = None,
) -> List[Issue]:
    """
    Retrieve a list of issues with pagination.
    """
    query = db.query(Issue)
    if project_id is not None:
        query = query.filter(Issue.project_id == project_id)
    return query.order_by(Issue.updated_at.desc(), Issue.id.desc()).offset(skip).limit(limit).all()


def create_issue(
    db: Session,
    issue: IssueCreate,
    reporter_id: int,
    project_id: Optional[int] = None,
) -> Issue:
    """
    Create a new issue.
    """
    if project_id is None:
        default_project = db.query(Project).filter(Project.key == "INSEED").first()
        project_id = default_project.id if default_project else None
    db_issue = Issue(
        title=issue.title,
        description=issue.description,
        status=issue.status,
        priority=issue.priority,
        reporter_id=reporter_id,
        assignee_id=issue.assignee_id,
        project_id=project_id,
    )
    db.add(db_issue)
    db.commit()
    db.refresh(db_issue)
    return db_issue


def update_issue(db: Session, issue_id: int, issue_in: IssueUpdate) -> Optional[Issue]:
    """
    Update an existing issue.
    """
    db_issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not db_issue:
        return None
    
    update_data = issue_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field in {"status", "priority"} and value is not None:
            value = value.value
        setattr(db_issue, field, value)
    
    db.add(db_issue)
    db.commit()
    db.refresh(db_issue)
    return db_issue


def remove_issue(db: Session, issue_id: int) -> Optional[Issue]:
    """
    Remove an issue from the database.
    """
    db_issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if db_issue:
        db.delete(db_issue)
        db.commit()
    return db_issue