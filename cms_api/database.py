import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# ── Database URL ─────────────────────────────────────────────
# Format: postgresql://user:password@host:port/dbname
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:Hype1204%40@127.0.0.1:5432/cms_db"
)

# ── Engine ───────────────────────────────────────────────────
# pool_size      : number of persistent connections kept open
# max_overflow   : extra connections allowed beyond pool_size under load
# pool_pre_ping  : test connection health before using (avoids stale connections)
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)

# ── Session Factory ──────────────────────────────────────────
# autocommit=False : we control when to commit (explicit is safer)
# autoflush=False  : don't auto-sync to DB before every query
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

# ── Base Class ───────────────────────────────────────────────
# All ORM models will inherit from this
class Base(DeclarativeBase):
    pass

# ── FastAPI Dependency ───────────────────────────────────────
# Inject this into routes using: db: Session = Depends(get_db)
# Opens a session, yields it, always closes it after the request
def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()   # rollback on any error
        raise
    finally:
        db.close()      # always close, success or failure