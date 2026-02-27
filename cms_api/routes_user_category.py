from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from config import get_conn
from models import UserCreate, UserUpdate, UserOut, CategoryCreate, CategoryUpdate, CategoryOut
from datetime import datetime, timezone

user_router     = APIRouter(prefix="/users",      tags=["Users"])
category_router = APIRouter(prefix="/categories", tags=["Categories"])

NOW = lambda: datetime.now(timezone.utc)

# ── USERS ────────────────────────────────────────────────────
@user_router.post("/", response_model=UserOut, status_code=201)
def create_user(payload: UserCreate, created_by: Optional[int] = Query(default=None)):
    with get_conn() as conn, conn.cursor() as cur:
        # Step 1: insert with created_by from query param (admin id) or NULL
        cur.execute(
            """INSERT INTO "user" (username,email,password,role,created_by,updated_by)
               VALUES (%s,%s,%s,%s,%s,%s) RETURNING *""",
            (payload.username, payload.email, payload.password,
             payload.role, created_by, created_by))
        user = dict(cur.fetchone())

        # Step 2: if no created_by param given, self-assign the new user's own id
        if created_by is None:
            cur.execute(
                """UPDATE "user" SET created_by=%s, updated_by=%s
                   WHERE user_id=%s RETURNING *""",
                (user["user_id"], user["user_id"], user["user_id"]))
            user = dict(cur.fetchone())

        return user

@user_router.get("/", response_model=list[UserOut])
def list_users():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute('SELECT * FROM "user" ORDER BY user_id')
        return [dict(r) for r in cur.fetchall()]

@user_router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute('SELECT * FROM "user" WHERE user_id=%s', (user_id,))
        row = cur.fetchone()
        if not row: raise HTTPException(404, "User not found")
        return dict(row)

@user_router.patch("/{user_id}", response_model=UserOut)
def update_user(user_id: int, payload: UserUpdate, updated_by: Optional[int] = Query(default=None)):
    fields = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not fields: raise HTTPException(400, "No fields to update")
    fields["updated_at"] = NOW()
    fields["updated_by"] = updated_by if updated_by else user_id
    cols = ", ".join(f"{k}=%s" for k in fields)
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(f'UPDATE "user" SET {cols} WHERE user_id=%s RETURNING *',
                    (*fields.values(), user_id))
        row = cur.fetchone()
        if not row: raise HTTPException(404, "User not found")
        return dict(row)

@user_router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute('DELETE FROM "user" WHERE user_id=%s', (user_id,))
        if cur.rowcount == 0: raise HTTPException(404, "User not found")


# ── CATEGORIES ───────────────────────────────────────────────
@category_router.post("/", response_model=CategoryOut, status_code=201)
def create_category(payload: CategoryCreate, created_by: Optional[int] = Query(default=None)):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO category (name,created_by,updated_by) VALUES (%s,%s,%s) RETURNING *",
            (payload.name, created_by, created_by))
        return dict(cur.fetchone())

@category_router.get("/", response_model=list[CategoryOut])
def list_categories():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM category ORDER BY category_id")
        return [dict(r) for r in cur.fetchall()]

@category_router.get("/{category_id}", response_model=CategoryOut)
def get_category(category_id: int):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM category WHERE category_id=%s", (category_id,))
        row = cur.fetchone()
        if not row: raise HTTPException(404, "Category not found")
        return dict(row)

@category_router.patch("/{category_id}", response_model=CategoryOut)
def update_category(category_id: int, payload: CategoryUpdate, updated_by: Optional[int] = Query(default=None)):
    fields = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not fields: raise HTTPException(400, "No fields to update")
    fields["updated_at"] = NOW()
    fields["updated_by"] = updated_by
    cols = ", ".join(f"{k}=%s" for k in fields)
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(f"UPDATE category SET {cols} WHERE category_id=%s RETURNING *",
                    (*fields.values(), category_id))
        row = cur.fetchone()
        if not row: raise HTTPException(404, "Category not found")
        return dict(row)

@category_router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM category WHERE category_id=%s", (category_id,))
        if cur.rowcount == 0: raise HTTPException(404, "Category not found")