from fastapi import APIRouter, HTTPException, Query
from config import get_conn
from models import UserCreate, UserUpdate, UserOut, CategoryCreate, CategoryUpdate, CategoryOut
from datetime import datetime, timezone

user_router = APIRouter(prefix="/users", tags=["Users"])
category_router = APIRouter(prefix="/categories", tags=["Categories"])

# ── USERS ────────────────────────────────────────────────────
@user_router.post("/", response_model=UserOut, status_code=201)
def create_user(payload: UserCreate, created_by: int = Query(None)):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """INSERT INTO "user" (username,email,password,role,created_by,updated_by)
               VALUES (%s,%s,%s,%s,%s,%s) RETURNING *""",
            (payload.username, payload.email, payload.password,
             payload.role, created_by, created_by))
        return dict(cur.fetchone())

@user_router.get("/", response_model=list[UserOut])
def list_users():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute('SELECT * FROM "user" ORDER BY user_id')
        return [dict(r) for r in cur.fetchall()]

@user_router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute('SELECT * FROM "user" WHERE user_id=%s', (user_id,))
        if not (row := cur.fetchone()): raise HTTPException(404, "User not found")
        return dict(row)

@user_router.patch("/{user_id}", response_model=UserOut)
def update_user(user_id: int, payload: UserUpdate, updated_by: int = Query(...)):
    fields = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
    if not fields: raise HTTPException(400, "No fields to update")
    fields["updated_at"], fields["updated_by"] = datetime.now(timezone.utc), updated_by
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(f'UPDATE "user" SET {",".join(f"{k}=%s" for k in fields)} WHERE user_id=%s RETURNING *',
                    (*fields.values(), user_id))
        if not (row := cur.fetchone()): raise HTTPException(404, "User not found")
        return dict(row)

@user_router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute('DELETE FROM "user" WHERE user_id=%s', (user_id,))
        if cur.rowcount == 0: raise HTTPException(404, "User not found")

# ── CATEGORIES ───────────────────────────────────────────────
@category_router.post("/", response_model=CategoryOut, status_code=201)
def create_category(payload: CategoryCreate, created_by: int = Query(...)):
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
        if not (row := cur.fetchone()): raise HTTPException(404, "Category not found")
        return dict(row)

@category_router.patch("/{category_id}", response_model=CategoryOut)
def update_category(category_id: int, payload: CategoryUpdate, updated_by: int = Query(...)):
    fields = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
    if not fields: raise HTTPException(400, "No fields to update")
    fields["updated_at"], fields["updated_by"] = datetime.now(timezone.utc), updated_by
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(f"UPDATE category SET {','.join(f'{k}=%s' for k in fields)} WHERE category_id=%s RETURNING *",
                    (*fields.values(), category_id))
        if not (row := cur.fetchone()): raise HTTPException(404, "Category not found")
        return dict(row)

@category_router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM category WHERE category_id=%s", (category_id,))
        if cur.rowcount == 0: raise HTTPException(404, "Category not found")