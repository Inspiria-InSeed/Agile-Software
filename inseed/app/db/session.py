from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings

connect_args = (
    {"check_same_thread": False}
    if settings.SQLALCHEMY_DATABASE_URI.startswith("sqlite")
    else {}
)
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    """
    Database session generator.
    Creates and yields a database session, ensuring it is closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()