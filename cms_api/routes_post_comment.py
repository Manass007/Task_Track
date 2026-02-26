from fastapi import APIRouter, HTTPException, Query
from config import get_conn
from models import PostCreate, PostUpdate, PostOut, CommentCreate, CommentUpdate, CommentOut
from datetime import datetime, timezone

post_router = APIRouter(prefix="/posts", tags=["Posts"])
comment_router = APIRouter(prefix="/comments", tags=["Comments"])

# ── POSTS ────────────────────────────────────────────────────
@post_router.post("/", response_model=PostOut, status_code=201)
def create_post(payload: PostCreate, created_by: int = Query(...)):
    pub = datetime.now(timezone.utc) if payload.status == "published" else None
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """INSERT INTO post (user_id,category_id,title,body,status,media_url,published_at,created_by,updated_by)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING *""",
            (payload.user_id, payload.category_id, payload.title, payload.body,
             payload.status, payload.media_url, pub, created_by, created_by))
        return dict(cur.fetchone())

@post_router.get("/", response_model=list[PostOut])
def list_posts(status: str = None):
    with get_conn() as conn, conn.cursor() as cur:
        query = "SELECT * FROM post WHERE status=%s ORDER BY post_id" if status else "SELECT * FROM post ORDER BY post_id"
        cur.execute(query, (status,) if status else ())
        return [dict(r) for r in cur.fetchall()]

@post_router.get("/{post_id}", response_model=PostOut)
def get_post(post_id: int):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM post WHERE post_id=%s", (post_id,))
        if not (row := cur.fetchone()): raise HTTPException(404, "Post not found")
        return dict(row)

@post_router.patch("/{post_id}", response_model=PostOut)
def update_post(post_id: int, payload: PostUpdate, updated_by: int = Query(...)):
    fields = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
    if not fields: raise HTTPException(400, "No fields to update")
    if fields.get("status") == "published": fields["published_at"] = datetime.now(timezone.utc)
    fields["updated_at"], fields["updated_by"] = datetime.now(timezone.utc), updated_by
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(f"UPDATE post SET {','.join(f'{k}=%s' for k in fields)} WHERE post_id=%s RETURNING *",
                    (*fields.values(), post_id))
        if not (row := cur.fetchone()): raise HTTPException(404, "Post not found")
        return dict(row)

@post_router.delete("/{post_id}", status_code=204)
def delete_post(post_id: int):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM post WHERE post_id=%s", (post_id,))
        if cur.rowcount == 0: raise HTTPException(404, "Post not found")

# ── COMMENTS ─────────────────────────────────────────────────
@comment_router.post("/", response_model=CommentOut, status_code=201)
def create_comment(payload: CommentCreate, created_by: int = Query(...)):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """INSERT INTO comment (post_id,user_id,category_id,body,created_by,updated_by)
               VALUES (%s,%s,%s,%s,%s,%s) RETURNING *""",
            (payload.post_id, payload.user_id, payload.category_id, payload.body, created_by, created_by))
        return dict(cur.fetchone())

@comment_router.get("/", response_model=list[CommentOut])
def list_comments(post_id: int = None):
    with get_conn() as conn, conn.cursor() as cur:
        query = "SELECT * FROM comment WHERE post_id=%s ORDER BY comment_id" if post_id else "SELECT * FROM comment ORDER BY comment_id"
        cur.execute(query, (post_id,) if post_id else ())
        return [dict(r) for r in cur.fetchall()]

@comment_router.get("/{comment_id}", response_model=CommentOut)
def get_comment(comment_id: int):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM comment WHERE comment_id=%s", (comment_id,))
        if not (row := cur.fetchone()): raise HTTPException(404, "Comment not found")
        return dict(row)

@comment_router.patch("/{comment_id}", response_model=CommentOut)
def update_comment(comment_id: int, payload: CommentUpdate, updated_by: int = Query(...)):
    fields = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
    if not fields: raise HTTPException(400, "No fields to update")
    fields["updated_at"], fields["updated_by"] = datetime.now(timezone.utc), updated_by
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(f"UPDATE comment SET {','.join(f'{k}=%s' for k in fields)} WHERE comment_id=%s RETURNING *",
                    (*fields.values(), comment_id))
        if not (row := cur.fetchone()): raise HTTPException(404, "Comment not found")
        return dict(row)

@comment_router.delete("/{comment_id}", status_code=204)
def delete_comment(comment_id: int):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM comment WHERE comment_id=%s", (comment_id,))
        if cur.rowcount == 0: raise HTTPException(404, "Comment not found")