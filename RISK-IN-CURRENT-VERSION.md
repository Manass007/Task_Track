# Why I'm Migrating My CMS API to SQLAlchemy

## Background

I built a REST API for a retail website blog using **FastAPI + PostgreSQL (psycopg2)**. The API covers four core entities — User, Category, Post, and Comment — with full CRUD operations. It works, but as I reviewed the codebase more closely, I realized I was carrying some real risks by writing raw SQL directly in my route handlers.

This document captures my understanding of what those risks are, why SQLAlchemy solves them, and how I'm thinking about the migration.

---

## What My Current Setup Looks Like

Right now, every route in my API works like this:

```
HTTP Request → Route Handler → f-string SQL → psycopg2 → dict → Pydantic Response
```

I have a `get_conn()` function in `config.py` that opens a fresh psycopg2 connection on every request, I write raw SQL strings directly in the route, and I return `dict(cur.fetchone())` to Pydantic for response validation.

It gets the job done, but here's where I'm exposed.

---

## The Risks I Identified in My Current Code

### 1. SQL Injection via Column Names

My `PATCH` endpoints dynamically build queries like this:

```python
fields = {k: v for k, v in payload.model_dump().items() if v is not None}
cols = ", ".join(f"{k}=%s" for k in fields)
cur.execute(f'UPDATE "user" SET {cols} WHERE user_id=%s RETURNING *', (*fields.values(), user_id))
```

The values are safely parameterized with `%s`, but the **column names** (`k`) are directly interpolated into the f-string. psycopg2 cannot parameterize column names — only values. If I ever expose a field that an attacker could control, or if I make a mistake in filtering model fields, this pattern is exploitable.

### 2. No Connection Pooling

Every single API request calls `get_conn()`, which opens a **brand new TCP connection** to Postgres and closes it when done. This is fine for low traffic, but it won't scale. Opening connections is expensive — it involves TCP handshaking, authentication, and process allocation on the Postgres side. Under any real load, this becomes a bottleneck.

### 3. Schema Lives Outside My Code

My database schema is defined in a separate `schema.sql` file. My Python models (Pydantic) are defined in `models.py`. These two things have no relationship to each other — they're just manually kept in sync by me. If I add a field to a Pydantic model and forget to update the SQL, the bug only shows up at runtime.

There's also no migration history. If I need to change a column type or add a table, I have no versioned record of what the database looked like before.

### 4. Two Sources of Truth for Timestamps

In some places, I'm computing `NOW()` in Python:

```python
NOW = lambda: datetime.now(timezone.utc)
fields["updated_at"] = NOW()
```

But in my schema, I also have:

```sql
updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
```

Two places managing the same thing means inconsistency risk — especially across timezones or if I ever run multiple instances.

### 5. Raw Dict Juggling

Returning `dict(cur.fetchone())` works, but it's fragile. I'm getting raw Python dicts from psycopg2 and relying entirely on Pydantic at the response layer to catch any mismatches. Nothing enforces types between the database and my route logic — the middle layer is untyped.

---

## What SQLAlchemy Is

SQLAlchemy is a Python **ORM (Object Relational Mapper)** and SQL toolkit. It lets me interact with the database using Python classes and objects instead of raw SQL strings. It operates at two levels:

- **Core** — A SQL expression builder that's pythonic but still close to SQL
- **ORM** — Full object mapping where tables become Python classes and rows become instances

For my FastAPI backend, I'll use the ORM layer with SQLAlchemy's `DeclarativeBase`, paired with a proper `Session` per request.

---

## How SQLAlchemy Fixes Each Problem

| Problem I Have                 | How SQLAlchemy Fixes It                                                     |
| ------------------------------ | --------------------------------------------------------------------------- |
| SQL injection via column names | ORM builds queries programmatically — no f-string column interpolation ever |
| No connection pooling          | Built-in `QueuePool` by default — connections are reused across requests    |
| Schema disconnected from code  | Declarative ORM models **are** the schema — one source of truth             |
| No migration history           | Pair with **Alembic** for versioned, trackable schema migrations            |
| Duplicate timestamp logic      | `server_default=func.now()`, `onupdate=func.now()` — DB handles it once     |
| Raw untyped dict juggling      | ORM returns typed model instances, not raw dicts                            |

---

## The Architecture Shift I'm Making

**Before:**

```
HTTP Request → Route → f-string SQL → psycopg2 → dict → Pydantic
```

**After:**

```
HTTP Request → Route → ORM Session → SQLAlchemy → typed ORM instance → Pydantic
```

My project structure will become:

```
cms_api/
├── main.py                  # FastAPI app (unchanged)
├── config.py                # DB URL config
├── database.py              # Engine + Session setup (new)
├── orm_models.py            # SQLAlchemy declarative models (replaces schema.sql)
├── models.py                # Pydantic request/response models (unchanged)
├── routes_user_category.py  # Updated to use ORM sessions
├── routes_post_comment.py   # Updated to use ORM sessions
└── requirements.txt
```

The key new file is `database.py`, which sets up the engine with connection pooling and provides a `get_db()` dependency that FastAPI will inject into each route — giving each request a proper session that commits on success and rolls back on failure.

---

## Why This Matters Beyond Just "Best Practice"

I'm not making this change just to follow convention. The raw SQL approach has a real ceiling:

- If I ever add a second API worker process, connection management becomes a problem immediately
- If I want to add schema migrations safely (without downtime or data loss), I have no path to do that today
- If someone audits this code, the dynamic column-name injection in PATCH endpoints is a flag

SQLAlchemy gives me the foundation to grow the project properly — with type safety, connection pooling, and a schema that lives alongside the code that uses it.

---
