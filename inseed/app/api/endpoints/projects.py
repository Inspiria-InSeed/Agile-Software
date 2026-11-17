from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import issue as crud_issue
from app.db.models import Project, User
from app.schemas.issue import Issue, IssueCreate
from app.schemas.project import ProjectCreate, ProjectRead

router = APIRouter()


@router.get("/", response_model=List[ProjectRead])
def read_projects(
    db: Session = Depends(deps.get_db),
    current_user: deps.models.User = Depends(deps.get_current_user),
) -> Any:
    return db.query(Project).order_by(Project.created_at.asc(), Project.id.asc()).all()


@router.post("/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(
    project_in: ProjectCreate,
    db: Session = Depends(deps.get_db),
    current_user: deps.models.User = Depends(deps.get_current_user),
) -> Any:
    if db.query(Project).filter(Project.key == project_in.key).first():
        raise HTTPException(status_code=409, detail="A project with this key already exists")
    project = Project(
        name=project_in.name,
        key=project_in.key,
        description=project_in.description,
        creator_id=current_user.id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/{project_id}/issues", response_model=List[Issue])
def read_project_issues(
    project_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: deps.models.User = Depends(deps.get_current_user),
) -> Any:
    if not db.query(Project.id).filter(Project.id == project_id).first():
        raise HTTPException(status_code=404, detail="Project not found")
    return crud_issue.get_issues(db, skip=skip, limit=limit, project_id=project_id)


@router.post(
    "/{project_id}/issues",
    response_model=Issue,
    status_code=status.HTTP_201_CREATED,
)
def create_project_issue(
    project_id: int,
    issue_in: IssueCreate,
    db: Session = Depends(deps.get_db),
    current_user: deps.models.User = Depends(deps.get_current_user),
) -> Any:
    if not db.query(Project.id).filter(Project.id == project_id).first():
        raise HTTPException(status_code=404, detail="Project not found")
    if issue_in.assignee_id is not None and not db.query(User.id).filter(
        User.id == issue_in.assignee_id
    ).first():
        raise HTTPException(status_code=404, detail="Assignee not found")
    return crud_issue.create_issue(
        db=db,
        issue=issue_in,
        reporter_id=current_user.id,
        project_id=project_id,
    )
