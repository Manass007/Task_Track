from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timezone

from database import get_db
from models import (
    PostCreate, PostUpdate, PostOut,
    CommentCreate, CommentUpdate, CommentOut,
    PostORM, CommentORM,
    PostStatus
)

post_router    = APIRouter(prefix="/posts",    tags=["Posts"])
comment_router = APIRouter(prefix="/comments", tags=["Comments"])


# ══════════════════════════════════════════════════════════════
#  POSTS
# ══════════════════════════════════════════════════════════════

@post_router.post("/", response_model=PostOut, status_code=201)
def create_post(
    payload: PostCreate,
    created_by: Optional[int] = Query(default=None),
    db: Session = Depends(get_db)
):
    post = PostORM(
        user_id      = payload.user_id,
        category_id  = payload.category_id,
        title        = payload.title,
        body         = payload.body,
        status       = payload.status,
        media_url    = payload.media_url,
        published_at = datetime.now(timezone.utc) if payload.status == PostStatus.published else None,
        created_by   = created_by,
        updated_by   = created_by,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


@post_router.get("/", response_model=list[PostOut])
def list_posts(
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(PostORM)
    if status:
        query = query.filter(PostORM.status == status)
    return query.order_by(PostORM.post_id).all()


@post_router.get("/{post_id}", response_model=PostOut)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(PostORM).filter(PostORM.post_id == post_id).first()
    if not post:
        raise HTTPException(404, "Post not found")
    return post


@post_router.patch("/{post_id}", response_model=PostOut)
def update_post(
    post_id: int,
    payload: PostUpdate,
    updated_by: Optional[int] = Query(default=None),
    db: Session = Depends(get_db)
):
    post = db.query(PostORM).filter(PostORM.post_id == post_id).first()
    if not post:
        raise HTTPException(404, "Post not found")

    fields = payload.model_dump(exclude_none=True)
    if not fields:
        raise HTTPException(400, "No fields to update")

    for key, value in fields.items():
        setattr(post, key, value)

    # if status is being changed to published, stamp published_at
    if fields.get("status") == PostStatus.published and not post.published_at:
        post.published_at = datetime.now(timezone.utc)

    post.updated_by = updated_by
    post.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(post)
    return post


@post_router.delete("/{post_id}", status_code=204)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(PostORM).filter(PostORM.post_id == post_id).first()
    if not post:
        raise HTTPException(404, "Post not found")
    db.delete(post)
    db.commit()


# ══════════════════════════════════════════════════════════════
#  COMMENTS
# ══════════════════════════════════════════════════════════════

@comment_router.post("/", response_model=CommentOut, status_code=201)
def create_comment(
    payload: CommentCreate,
    created_by: Optional[int] = Query(default=None),
    db: Session = Depends(get_db)
):
    comment = CommentORM(
        post_id     = payload.post_id,
        user_id     = payload.user_id,
        category_id = payload.category_id,
        body        = payload.body,
        created_by  = created_by,
        updated_by  = created_by,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


@comment_router.get("/", response_model=list[CommentOut])
def list_comments(
    post_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(CommentORM)
    if post_id:
        query = query.filter(CommentORM.post_id == post_id)
    return query.order_by(CommentORM.comment_id).all()


@comment_router.get("/{comment_id}", response_model=CommentOut)
def get_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = db.query(CommentORM).filter(CommentORM.comment_id == comment_id).first()
    if not comment:
        raise HTTPException(404, "Comment not found")
    return comment


@comment_router.patch("/{comment_id}", response_model=CommentOut)
def update_comment(
    comment_id: int,
    payload: CommentUpdate,
    updated_by: Optional[int] = Query(default=None),
    db: Session = Depends(get_db)
):
    comment = db.query(CommentORM).filter(CommentORM.comment_id == comment_id).first()
    if not comment:
        raise HTTPException(404, "Comment not found")

    fields = payload.model_dump(exclude_none=True)
    if not fields:
        raise HTTPException(400, "No fields to update")

    for key, value in fields.items():
        setattr(comment, key, value)

    comment.updated_by = updated_by
    comment.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(comment)
    return comment


@comment_router.delete("/{comment_id}", status_code=204)
def delete_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = db.query(CommentORM).filter(CommentORM.comment_id == comment_id).first()
    if not comment:
        raise HTTPException(404, "Comment not found")
    db.delete(comment)
    db.commit()