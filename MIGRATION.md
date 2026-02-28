# PostgreSQL Schema Migration — `public` → `mg_schema`

**Project:** CMS API (`cms_db`)  
**Purpose:** Isolate project tables and types from the default `public` schema into a dedicated `mg_schema`.

---

## Overview

By default, PostgreSQL places all objects in the `public` schema. This migration moves all project-specific tables, types, and sequences into `mg_schema` for better isolation, security, and maintainability.

---

## Step 1: Connect to the Database

```bash
psql -U your_username -d cms_db
```

---

## Step 2: Create the New Schema

```sql
CREATE SCHEMA mg_schema;
```

---

## Step 3: Inspect Existing Objects in `public`

**Check tables:**

```sql
SELECT tablename FROM pg_tables WHERE schemaname = 'public';
```

**Check custom types (enums/composites):**

```sql
SELECT typname, typtype FROM pg_type
JOIN pg_namespace ON pg_namespace.oid = pg_type.typnamespace
WHERE pg_namespace.nspname = 'public'
AND typtype IN ('e', 'c');
```

> **Note:** The filter `pg_type.typowner != 10` may exclude types owned by the superuser (OID 10). Always use `typtype IN ('e', 'c')` instead to get all custom enums and composites regardless of ownership.

**Check sequences:**

```sql
SELECT sequencename FROM pg_sequences WHERE schemaname = 'public';
```

---

## Step 4: Move Types First (Before Tables)

Types must be moved **before** the tables that depend on them, otherwise you'll get dependency errors.

```sql
ALTER TYPE public.post_status SET SCHEMA mg_schema;
ALTER TYPE public.user_role SET SCHEMA mg_schema;
```

---

## Step 5: Move Tables

```sql
ALTER TABLE public.user SET SCHEMA mg_schema;
ALTER TABLE public.category SET SCHEMA mg_schema;
ALTER TABLE public.post SET SCHEMA mg_schema;
ALTER TABLE public.comment SET SCHEMA mg_schema;
```

> **Note:** When tables are moved, their associated sequences (created via `SERIAL` or `BIGSERIAL`) are automatically moved along with them. You do **not** need to run `ALTER SEQUENCE` separately — attempting to do so will result in the error below.

---

## Errors Encountered

### Error 2: Custom Types Returning 0 Rows

Running the following query returned no results even though types existed:

```sql
SELECT typname, typtype FROM pg_type
JOIN pg_namespace ON pg_namespace.oid = pg_type.typnamespace
WHERE pg_namespace.nspname = 'public' AND pg_type.typowner != 10;
-- (0 rows)
```

**Cause:** The types `post_status` and `user_role` were owned by the superuser whose role OID is `10`, so they were filtered out.

**Resolution:** Remove the `typowner` filter and use `typtype IN ('e', 'c')` instead:

```sql
SELECT typname, typtype FROM pg_type
JOIN pg_namespace ON pg_namespace.oid = pg_type.typnamespace
WHERE pg_namespace.nspname = 'public'
AND typtype IN ('e', 'c');
```

---

### Error 3: FastAPI 500 — `relation "user" does not exist`

After migration, hitting the `POST /users/` endpoint from FastAPI returned:

```
INFO:     127.0.0.1:60016 - "POST /users/ HTTP/1.1" 500 Internal Server Error
psycopg2.errors.UndefinedTable: relation "user" does not exist
LINE 1: INSERT INTO "user" (username,email,password,role,created_by,...
```

**Server run command:**

```bash
uvicorn main:app --reload --port 8000
```

**Cause:** The tables were successfully moved to `mg_schema`, but the database `search_path` still pointed to `public`. PostgreSQL couldn't find the `user` table because it was no longer in `public`.

**Resolution:** Update the `search_path` so PostgreSQL looks in `mg_schema` first:

```sql
-- For the entire database (recommended)
ALTER DATABASE cms_db SET search_path TO mg_schema, public;
```

Then restart the FastAPI server:

```bash
uvicorn main:app --reload --port 8000
```

---

## Step 6: Update `search_path`

```sql
ALTER DATABASE cms_db SET search_path TO mg_schema, public;
```

---

## Step 8: Verify Migration

```sql
-- Should return 0 rows (public should be empty)
SELECT tablename FROM pg_tables WHERE schemaname = 'public';

-- Should list all 4 tables
SELECT tablename FROM pg_tables WHERE schemaname = 'mg_schema';

-- Should list all sequences
SELECT sequencename FROM pg_sequences WHERE schemaname = 'mg_schema';

-- Should list post_status and user_role
SELECT typname FROM pg_type
JOIN pg_namespace ON pg_namespace.oid = pg_type.typnamespace
WHERE pg_namespace.nspname = 'mg_schema' AND typtype IN ('e', 'c');
```

---

## Summary of Migrated Objects

| Object Type | Name                                         |
| ----------- | -------------------------------------------- |
| Table       | `user`                                       |
| Table       | `category`                                   |
| Table       | `post`                                       |
| Table       | `comment`                                    |
| Enum Type   | `post_status`                                |
| Enum Type   | `user_role`                                  |
| Sequence    | `user_user_id_seq` _(auto-migrated)_         |
| Sequence    | `category_category_id_seq` _(auto-migrated)_ |
| Sequence    | `post_post_id_seq` _(auto-migrated)_         |
| Sequence    | `comment_comment_id_seq` _(auto-migrated)_   |

---
