from pathlib import Path
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect

from app.api.endpoints import issues, projects, users
from app.core.config import settings
from app.db.models import Base, Issue, Project
from app.db.session import SessionLocal, engine

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STATIC_DIR = PROJECT_ROOT / "static"

def initialize_database() -> None:
    Base.metadata.create_all(bind=engine)
    issue_columns = {column["name"] for column in inspect(engine).get_columns("issues")}
    if "project_id" not in issue_columns:
        with engine.begin() as connection:
            connection.exec_driver_sql(
                "ALTER TABLE issues ADD COLUMN project_id INTEGER REFERENCES projects(id)"
            )

    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.key == "INSEED").first()
        if project is None:
            project = Project(name="Inseed", key="INSEED", description="Your Inseed project workspace")
            db.add(project)
            db.flush()
        db.query(Issue).filter(Issue.project_id.is_(None)).update(
            {Issue.project_id: project.id},
            synchronize_session=False,
        )
        db.commit()
    finally:
        db.close()


initialize_database()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(projects.router, prefix=f"{settings.API_V1_STR}/projects", tags=["projects"])
app.include_router(issues.router, prefix=f"{settings.API_V1_STR}/issues", tags=["issues"])


@app.middleware("http")
async def add_security_headers(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; connect-src 'self'; object-src 'none'; "
        "base-uri 'self'; form-action 'self'; frame-ancestors 'none'"
    )
    return response


@app.get("/", include_in_schema=False)
def home() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
