import enum
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy import Integer, String, Text, Enum as SAEnum, ForeignKey, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import TIMESTAMP

from database import Base


# ═══════════════════════════════════════════════════════════════
#  SECTION 1 — SHARED ENUMS
#  Used by both Pydantic models and SQLAlchemy ORM models
# ═══════════════════════════════════════════════════════════════

class UserRole(str, enum.Enum):
    admin  = "admin"
    author = "author"

class PostStatus(str, enum.Enum):
    draft     = "draft"
    published = "published"


# ═══════════════════════════════════════════════════════════════
#  SECTION 2 — PYDANTIC MODELS  (request / response validation)
# ═══════════════════════════════════════════════════════════════

# ── USER ────────────────────────────────────────────────────
class UserCreate(BaseModel):
    username: str
    email:    EmailStr
    password: str
    role:     UserRole = UserRole.author

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

    model_config = {"from_attributes": True}  # allows ORM instance → Pydantic


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

    model_config = {"from_attributes": True}


# ── POST ────────────────────────────────────────────────────
class PostCreate(BaseModel):
    user_id:     int
    category_id: int
    title:       str
    body:        str
    status:      PostStatus     = PostStatus.draft
    media_url:   Optional[str]  = None

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

    model_config = {"from_attributes": True}


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

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════
#  SECTION 3 — SQLALCHEMY ORM MODELS  (database tables)
#  All tables live in mg_schema
#  Enums live in public schema (already exist in DB, create_type=False)
# ═══════════════════════════════════════════════════════════════

def _utcnow():
    return datetime.now(timezone.utc)

# Reuse existing DB enums from public schema — do NOT recreate them
user_role_enum   = SAEnum(UserRole,   name="user_role",   schema="public", create_type=False)
post_status_enum = SAEnum(PostStatus, name="post_status", schema="public", create_type=False)


# ── USER ORM ─────────────────────────────────────────────────
class UserORM(Base):
    __tablename__ = "user"
    __table_args__ = (
        {"schema": "mg_schema"},
    )

    user_id    : Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    username   : Mapped[str]           = mapped_column(String(100), nullable=False)
    email      : Mapped[str]           = mapped_column(String(255), nullable=False, unique=True)
    password   : Mapped[str]           = mapped_column(Text, nullable=False)
    role       : Mapped[UserRole]      = mapped_column(user_role_enum, nullable=False, default=UserRole.author)
    created_at : Mapped[datetime]      = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    created_by : Mapped[int | None]    = mapped_column(Integer, ForeignKey("mg_schema.user.user_id"), nullable=True)
    updated_at : Mapped[datetime]      = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=_utcnow)
    updated_by : Mapped[int | None]    = mapped_column(Integer, ForeignKey("mg_schema.user.user_id"), nullable=True)

    posts    : Mapped[list["PostORM"]]    = relationship("PostORM",    back_populates="author",    foreign_keys="PostORM.user_id")
    comments : Mapped[list["CommentORM"]] = relationship("CommentORM", back_populates="commenter", foreign_keys="CommentORM.user_id")


# ── CATEGORY ORM ─────────────────────────────────────────────
class CategoryORM(Base):
    __tablename__ = "category"
    __table_args__ = (
        {"schema": "mg_schema"},
    )

    category_id : Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    name        : Mapped[str]           = mapped_column(String(150), nullable=False, unique=True)
    created_at  : Mapped[datetime]      = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    created_by  : Mapped[int | None]    = mapped_column(Integer, ForeignKey("mg_schema.user.user_id"), nullable=True)
    updated_at  : Mapped[datetime]      = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=_utcnow)
    updated_by  : Mapped[int | None]    = mapped_column(Integer, ForeignKey("mg_schema.user.user_id"), nullable=True)

    posts    : Mapped[list["PostORM"]]    = relationship("PostORM",    back_populates="category")
    comments : Mapped[list["CommentORM"]] = relationship("CommentORM", back_populates="category")


# ── POST ORM ─────────────────────────────────────────────────
class PostORM(Base):
    __tablename__ = "post"
    __table_args__ = (
        Index("idx_post_user",     "user_id"),
        Index("idx_post_category", "category_id"),
        {"schema": "mg_schema"},  # dict MUST be last
    )

    post_id      : Mapped[int]             = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id      : Mapped[int]             = mapped_column(Integer, ForeignKey("mg_schema.user.user_id"), nullable=False)
    category_id  : Mapped[int]             = mapped_column(Integer, ForeignKey("mg_schema.category.category_id"), nullable=False)
    title        : Mapped[str]             = mapped_column(String(255), nullable=False)
    body         : Mapped[str]             = mapped_column(Text, nullable=False)
    status       : Mapped[PostStatus]      = mapped_column(post_status_enum, nullable=False, default=PostStatus.draft)
    media_url    : Mapped[str | None]      = mapped_column(Text, nullable=True)
    published_at : Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    created_at   : Mapped[datetime]        = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    created_by   : Mapped[int | None]      = mapped_column(Integer, ForeignKey("mg_schema.user.user_id"), nullable=True)
    updated_at   : Mapped[datetime]        = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=_utcnow)
    updated_by   : Mapped[int | None]      = mapped_column(Integer, ForeignKey("mg_schema.user.user_id"), nullable=True)

    author   : Mapped["UserORM"]              = relationship("UserORM",     back_populates="posts",    foreign_keys=[user_id])
    category : Mapped["CategoryORM"]          = relationship("CategoryORM", back_populates="posts")
    comments : Mapped[list["CommentORM"]]     = relationship("CommentORM",  back_populates="post", cascade="all, delete-orphan")


# ── COMMENT ORM ──────────────────────────────────────────────
class CommentORM(Base):
    __tablename__ = "comment"
    __table_args__ = (
        Index("idx_comment_post", "post_id"),
        Index("idx_comment_user", "user_id"),
        {"schema": "mg_schema"},  # dict MUST be last
    )

    comment_id  : Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    post_id     : Mapped[int]           = mapped_column(Integer, ForeignKey("mg_schema.post.post_id", ondelete="CASCADE"), nullable=False)
    user_id     : Mapped[int]           = mapped_column(Integer, ForeignKey("mg_schema.user.user_id"), nullable=False)
    category_id : Mapped[int]           = mapped_column(Integer, ForeignKey("mg_schema.category.category_id"), nullable=False)
    body        : Mapped[str]           = mapped_column(Text, nullable=False)
    created_at  : Mapped[datetime]      = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    created_by  : Mapped[int | None]    = mapped_column(Integer, ForeignKey("mg_schema.user.user_id"), nullable=True)
    updated_at  : Mapped[datetime]      = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=_utcnow)
    updated_by  : Mapped[int | None]    = mapped_column(Integer, ForeignKey("mg_schema.user.user_id"), nullable=True)

    post      : Mapped["PostORM"]     = relationship("PostORM",     back_populates="comments")
    commenter : Mapped["UserORM"]     = relationship("UserORM",     back_populates="comments", foreign_keys=[user_id])
    category  : Mapped["CategoryORM"] = relationship("CategoryORM", back_populates="comments")