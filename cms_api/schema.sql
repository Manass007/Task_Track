-- ============================================================
-- CMS Schema — Retail Website Blog
-- Run:  psql -U postgres -d cms_db -f schema.sql
-- ============================================================

-- ENUM types
DO $$ BEGIN
    CREATE TYPE user_role   AS ENUM ('admin', 'author');
    CREATE TYPE post_status AS ENUM ('draft', 'published');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- ── USER ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS "user" (
    user_id       SERIAL          PRIMARY KEY,
    username      VARCHAR(100)    NOT NULL,
    email         VARCHAR(255)    NOT NULL UNIQUE,
    password_hash TEXT            NOT NULL,
    role          user_role       NOT NULL DEFAULT 'author',
    created_at    TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    created_by    INT             REFERENCES "user"(user_id),
    updated_at    TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_by    INT             REFERENCES "user"(user_id)
);

-- ── CATEGORY ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS category (
    category_id SERIAL          PRIMARY KEY,
    name        VARCHAR(150)    NOT NULL UNIQUE,
    created_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    created_by  INT             REFERENCES "user"(user_id),
    updated_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_by  INT             REFERENCES "user"(user_id)
);

-- ── POST ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS post (
    post_id      SERIAL          PRIMARY KEY,
    user_id      INT             NOT NULL REFERENCES "user"(user_id),
    category_id  INT             NOT NULL REFERENCES category(category_id),
    title        VARCHAR(255)    NOT NULL,
    body         TEXT            NOT NULL,
    status       post_status     NOT NULL DEFAULT 'draft',
    media_url    TEXT,
    published_at TIMESTAMPTZ,
    created_at   TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    created_by   INT             REFERENCES "user"(user_id),
    updated_at   TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_by   INT             REFERENCES "user"(user_id)
);

-- ── COMMENT ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS comment (
    comment_id  SERIAL          PRIMARY KEY,
    post_id     INT             NOT NULL REFERENCES post(post_id) ON DELETE CASCADE,
    user_id     INT             NOT NULL REFERENCES "user"(user_id),
    category_id INT             NOT NULL REFERENCES category(category_id),
    body        TEXT            NOT NULL,
    created_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    created_by  INT             REFERENCES "user"(user_id),
    updated_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_by  INT             REFERENCES "user"(user_id)
);

-- ── INDEXES ─────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_post_user     ON post(user_id);
CREATE INDEX IF NOT EXISTS idx_post_category ON post(category_id);
CREATE INDEX IF NOT EXISTS idx_comment_post  ON comment(post_id);
CREATE INDEX IF NOT EXISTS idx_comment_user  ON comment(user_id);