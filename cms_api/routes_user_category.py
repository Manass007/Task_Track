from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timezone

from database import get_db
from models import (
    UserCreate, UserUpdate, UserOut,
    CategoryCreate, CategoryUpdate, CategoryOut,
    UserORM, CategoryORM
)

user_router     = APIRouter(prefix="/users",      tags=["Users"])
category_router = APIRouter(prefix="/categories", tags=["Categories"])


# ══════════════════════════════════════════════════════════════
#  USERS
# ══════════════════════════════════════════════════════════════

@user_router.post("/", response_model=UserOut, status_code=201)
def create_user(
    payload: UserCreate,
    created_by: Optional[int] = Query(default=None),
    db: Session = Depends(get_db)
):
    user = UserORM(
        username   = payload.username,
        email      = payload.email,
        password   = payload.password,
        role       = payload.role,
        created_by = created_by,
        updated_by = created_by,
    )
    db.add(user)
    db.flush()  # flush to get user.user_id before commit

    # if no created_by given, self-assign the new user's own id
    if created_by is None:
        user.created_by = user.user_id
        user.updated_by = user.user_id

    db.commit()
    db.refresh(user)
    return user


@user_router.get("/", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db)):
    return db.query(UserORM).order_by(UserORM.user_id).all()


@user_router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserORM).filter(UserORM.user_id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    return user


@user_router.patch("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    payload: UserUpdate,
    updated_by: Optional[int] = Query(default=None),
    db: Session = Depends(get_db)
):
    user = db.query(UserORM).filter(UserORM.user_id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    fields = payload.model_dump(exclude_none=True)
    if not fields:
        raise HTTPException(400, "No fields to update")

    for key, value in fields.items():
        setattr(user, key, value)

    user.updated_by = updated_by if updated_by else user_id
    user.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(user)
    return user


@user_router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserORM).filter(UserORM.user_id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    db.delete(user)
    db.commit()


# ══════════════════════════════════════════════════════════════
#  CATEGORIES
# ══════════════════════════════════════════════════════════════

@category_router.post("/", response_model=CategoryOut, status_code=201)
def create_category(
    payload: CategoryCreate,
    created_by: Optional[int] = Query(default=None),
    db: Session = Depends(get_db)
):
    category = CategoryORM(
        name       = payload.name,
        created_by = created_by,
        updated_by = created_by,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@category_router.get("/", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.query(CategoryORM).order_by(CategoryORM.category_id).all()


@category_router.get("/{category_id}", response_model=CategoryOut)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(CategoryORM).filter(CategoryORM.category_id == category_id).first()
    if not category:
        raise HTTPException(404, "Category not found")
    return category


@category_router.patch("/{category_id}", response_model=CategoryOut)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    updated_by: Optional[int] = Query(default=None),
    db: Session = Depends(get_db)
):
    category = db.query(CategoryORM).filter(CategoryORM.category_id == category_id).first()
    if not category:
        raise HTTPException(404, "Category not found")

    fields = payload.model_dump(exclude_none=True)
    if not fields:
        raise HTTPException(400, "No fields to update")

    for key, value in fields.items():
        setattr(category, key, value)

    category.updated_by = updated_by
    category.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(category)
    return category


@category_router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(CategoryORM).filter(CategoryORM.category_id == category_id).first()
    if not category:
        raise HTTPException(404, "Category not found")
    db.delete(category)
    db.commit()