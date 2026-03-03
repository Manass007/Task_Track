from fastapi import FastAPI
from database import engine, Base
from routes_user_category import user_router, category_router
from routes_post_comment   import post_router, comment_router

# Import all ORM models so Base.metadata knows about them
# This ensures create_all() picks up every table
from models import UserORM, CategoryORM, PostORM, CommentORM

app = FastAPI(
    title="CMS API — Retail Website Blog",
    description="CRUD API for USER · CATEGORY · POST · COMMENT",
    version="2.0.0",
)

@app.on_event("startup")
def startup():
    # Creates tables if they don't exist yet
    # Safe to run on every startup — won't touch existing tables
    # In production, prefer: alembic upgrade head (already done)
    Base.metadata.create_all(bind=engine)

app.include_router(user_router)
app.include_router(category_router)
app.include_router(post_router)
app.include_router(comment_router)

@app.get("/", tags=["Health"])
def health():
    return {"status": "ok", "message": "CMS API is running — SQLAlchemy ORM active"}