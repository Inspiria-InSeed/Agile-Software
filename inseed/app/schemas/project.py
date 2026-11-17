import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    key: str = Field(min_length=2, max_length=10)
    description: Optional[str] = Field(default=None, max_length=2000)

    @field_validator("name", "key")
    @classmethod
    def strip_value(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be blank")
        return value

    @field_validator("key")
    @classmethod
    def validate_key(cls, value: str) -> str:
        value = value.upper()
        if not re.fullmatch(r"[A-Z][A-Z0-9]{1,9}", value):
            raise ValueError("Project key must be 2–10 letters or numbers and start with a letter")
        return value


class ProjectRead(BaseModel):
    id: int
    name: str
    key: str
    description: Optional[str] = None
    created_at: datetime
    creator_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
