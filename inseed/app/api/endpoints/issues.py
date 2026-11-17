from typing import List, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.db.models import Comment, Issue, User
from app.crud import issue as crud_issue
from app.schemas.issue import CommentCreate, CommentRead, Issue, IssueCreate, IssueUpdate

router = APIRouter()


@router.get("/", response_model=List[Issue])
def read_issues(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: deps.models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve issues with pagination.
    """
    issues = crud_issue.get_issues(db, skip=skip, limit=limit)
    return issues


@router.post("/", response_model=Issue, status_code=status.HTTP_201_CREATED)
def create_issue(
    *,
    db: Session = Depends(deps.get_db),
    issue_in: IssueCreate,
    current_user: deps.models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Create new issue.
    """
    if issue_in.assignee_id is not None and not db.query(User).filter(
        User.id == issue_in.assignee_id
    ).first():
        raise HTTPException(status_code=404, detail="Assignee not found")
    issue = crud_issue.create_issue(
        db=db, issue=issue_in, reporter_id=current_user.id
    )
    return issue


@router.get("/{issue_id}", response_model=Issue)
def read_issue_by_id(
    issue_id: int,
    db: Session = Depends(deps.get_db),
    current_user: deps.models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Get issue by ID.
    """
    issue = crud_issue.get_issue(db=db, issue_id=issue_id)
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found",
        )
    return issue


@router.put("/{issue_id}", response_model=Issue)
def update_issue(
    *,
    db: Session = Depends(deps.get_db),
    issue_id: int,
    issue_in: IssueUpdate,
    current_user: deps.models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Update an issue.
    """
    update_data = issue_in.model_dump(exclude_unset=True)
    if update_data.get("assignee_id") is not None and not db.query(User).filter(
        User.id == update_data["assignee_id"]
    ).first():
        raise HTTPException(status_code=404, detail="Assignee not found")
    issue = crud_issue.update_issue(db=db, issue_id=issue_id, issue_in=issue_in)
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found",
        )
    return issue


@router.get("/{issue_id}/comments", response_model=List[CommentRead])
def read_issue_comments(
    issue_id: int,
    db: Session = Depends(deps.get_db),
    current_user: deps.models.User = Depends(deps.get_current_user),
) -> Any:
    issue = crud_issue.get_issue(db=db, issue_id=issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    comments = (
        db.query(Comment)
        .filter(Comment.issue_id == issue_id)
        .order_by(Comment.created_at.asc(), Comment.id.asc())
        .all()
    )
    return [
        {
            "id": comment.id,
            "body": comment.body,
            "created_at": comment.created_at,
            "author_id": comment.author_id,
            "author_name": comment.author.full_name or comment.author.email,
        }
        for comment in comments
    ]


@router.post(
    "/{issue_id}/comments",
    response_model=CommentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_issue_comment(
    issue_id: int,
    comment_in: CommentCreate,
    db: Session = Depends(deps.get_db),
    current_user: deps.models.User = Depends(deps.get_current_user),
) -> Any:
    if not crud_issue.get_issue(db=db, issue_id=issue_id):
        raise HTTPException(status_code=404, detail="Issue not found")
    comment = Comment(
        issue_id=issue_id,
        author_id=current_user.id,
        body=comment_in.body.strip(),
    )
    if not comment.body:
        raise HTTPException(status_code=422, detail="Comment cannot be blank")
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return {
        "id": comment.id,
        "body": comment.body,
        "created_at": comment.created_at,
        "author_id": comment.author_id,
        "author_name": current_user.full_name or current_user.email,
    }


@router.delete("/{issue_id}", response_model=Issue)
def delete_issue(
    *,
    db: Session = Depends(deps.get_db),
    issue_id: int,
    current_user: deps.models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Delete an issue.
    """
    issue = crud_issue.remove_issue(db=db, issue_id=issue_id)
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found",
        )
    return issue