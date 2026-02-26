from fastapi import FastAPI
from routes_user_category import user_router, category_router
from routes_post_comment   import post_router, comment_router

app = FastAPI(
    title="CMS API — Retail Website Blog",
    description="CRUD API for USER · CATEGORY · POST · COMMENT",
    version="1.0.0",
)

app.include_router(user_router)
app.include_router(category_router)
app.include_router(post_router)
app.include_router(comment_router)

@app.get("/", tags=["Health"])
def health():
    return {"status": "ok", "message": "CMS API is running"}