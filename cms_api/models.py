from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator


# ── Enums ────────────────────────────────────────────────────
class UserRole(str, Enum):
    admin  = "admin"
    author = "author"

class PostStatus(str, Enum):
    draft     = "draft"
    published = "published"


# ── USER ────────────────────────────────────────────────────
class UserCreate(BaseModel):
    username:      str
    email:         EmailStr
    password: str
    role:          UserRole = UserRole.author

    @field_validator("username")
    @classmethod
    def username_not_empty(cls, v):
        if not v.strip():
            raise ValueError("username must not be blank")
        return v.strip()

class UserUpdate(BaseModel):
    username: Optional[str]      = None
    email:    Optional[EmailStr] = None
    role:     Optional[UserRole] = None

class UserOut(BaseModel):
    user_id:    int
    username:   str
    email:      str
    role:       UserRole
    created_at: datetime
    updated_at: datetime


# ── CATEGORY ────────────────────────────────────────────────
class CategoryCreate(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError("category name must not be blank")
        return v.strip()

class CategoryUpdate(BaseModel):
    name: Optional[str] = None

class CategoryOut(BaseModel):
    category_id: int
    name:        str
    created_at:  datetime
    updated_at:  datetime


# ── POST ────────────────────────────────────────────────────
class PostCreate(BaseModel):
    user_id:     int
    category_id: int
    title:       str
    body:        str
    status:      PostStatus    = PostStatus.draft
    media_url:   Optional[str] = None

    @field_validator("title", "body")
    @classmethod
    def not_empty(cls, v):
        if not v.strip():
            raise ValueError("field must not be blank")
        return v.strip()

class PostUpdate(BaseModel):
    category_id: Optional[int]        = None
    title:       Optional[str]        = None
    body:        Optional[str]        = None
    status:      Optional[PostStatus] = None
    media_url:   Optional[str]        = None

class PostOut(BaseModel):
    post_id:      int
    user_id:      int
    category_id:  int
    title:        str
    body:         str
    status:       PostStatus
    media_url:    Optional[str]
    published_at: Optional[datetime]
    created_at:   datetime
    updated_at:   datetime


# ── COMMENT ─────────────────────────────────────────────────
class CommentCreate(BaseModel):
    post_id:     int
    user_id:     int
    category_id: int
    body:        str

    @field_validator("body")
    @classmethod
    def body_not_empty(cls, v):
        if not v.strip():
            raise ValueError("comment body must not be blank")
        return v.strip()

class CommentUpdate(BaseModel):
    body:        Optional[str] = None
    category_id: Optional[int] = None

class CommentOut(BaseModel):
    comment_id:  int
    post_id:     int
    user_id:     int
    category_id: int
    body:        str
    created_at:  datetime
    updated_at:  datetime