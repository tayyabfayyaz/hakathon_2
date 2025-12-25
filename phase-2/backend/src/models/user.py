from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field
from pydantic import EmailStr


class UserBase(SQLModel):
    email: str = Field(max_length=255, index=True, unique=True)


class User(UserBase, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    password_hash: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login_at: Optional[datetime] = None


class UserCreate(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)


class UserLogin(SQLModel):
    email: EmailStr
    password: str


class UserRead(SQLModel):
    id: UUID
    email: str
    created_at: datetime
