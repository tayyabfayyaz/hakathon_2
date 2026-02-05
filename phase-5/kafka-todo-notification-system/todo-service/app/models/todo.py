from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class TodoBase(BaseModel):
    title: str
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    priority: str = "normal"


class TodoCreate(TodoBase):
    user_id: str


class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    priority: Optional[str] = None


class Todo(TodoBase):
    id: str
    user_id: str
    status: str = "pending"
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True