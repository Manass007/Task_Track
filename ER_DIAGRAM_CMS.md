# CMS Entities & Relationships — Retail Website Blog

---

## 1. Research: Entities in a Content Management System

An **entity** in a CMS is any distinct object or concept that needs to be stored and managed. Below are the core entities found across most CMS platforms, along with their typical attributes.

---

### USER

Represents anyone who interacts with the CMS backend — admins and authors only.

| Attribute     | Type / Constraint        | Description                  |
| ------------- | ------------------------ | ---------------------------- |
| user_id       | PK                       | Unique identifier            |
| username      | VARCHAR                  | Display name                 |
| email         | VARCHAR · **UNIQUE**     | Login email — must be unique |
| password_hash | TEXT                     | Encrypted password           |
| role          | ENUM (`admin`, `author`) | Access level                 |
| created_at    | TIMESTAMPTZ              | Account creation timestamp   |
| created_by    | INT · FK → USER          | Who created this user        |
| updated_at    | TIMESTAMPTZ              | Last update timestamp        |
| updated_by    | INT · FK → USER          | Who last updated this user   |

> `role` is an **ENUM** with only two values: `admin` and `author`. Editor and subscriber have been removed.

---

### POST

The central entity — a blog article with an optional media attachment.

| Attribute    | Type / Constraint           | Description                         |
| ------------ | --------------------------- | ----------------------------------- |
| post_id      | PK                          | Unique identifier                   |
| user_id      | FK → USER                   | Who wrote this post                 |
| category_id  | FK → CATEGORY               | Which category it belongs to        |
| title        | VARCHAR                     | Post headline                       |
| body         | TEXT                        | Main content (rich text)            |
| status       | ENUM (`draft`, `published`) | Publication state                   |
| media_url    | TEXT                        | URL of attached image or media file |
| published_at | TIMESTAMPTZ                 | Publication timestamp               |
| created_at   | TIMESTAMPTZ                 | Creation timestamp                  |
| created_by   | INT · FK → USER             | Who created this post               |
| updated_at   | TIMESTAMPTZ                 | Last update timestamp               |
| updated_by   | INT · FK → USER             | Who last updated this post          |

---

### CATEGORY

Organizes posts into broad topics (e.g., "Shoes", "Skincare Tips").

| Attribute   | Type / Constraint    | Description                     |
| ----------- | -------------------- | ------------------------------- |
| category_id | PK                   | Unique identifier               |
| name        | VARCHAR · **UNIQUE** | Category label — must be unique |
| created_at  | TIMESTAMPTZ          | Creation timestamp              |
| created_by  | INT · FK → USER      | Who created this category       |
| updated_at  | TIMESTAMPTZ          | Last update timestamp           |
| updated_by  | INT · FK → USER      | Who last updated this category  |

---

### TAG

Fine-grained labels attached to posts (e.g., "summer", "sale", "trending").

| Attribute | Description                     |
| --------- | ------------------------------- |
| tag_id    | Unique identifier (Primary Key) |
| name      | Tag label                       |
| slug      | URL-friendly name               |

---

### COMMENT

Reader responses on a published post, categorized directly via CATEGORY.

| Attribute   | Type / Constraint | Description                        |
| ----------- | ----------------- | ---------------------------------- |
| comment_id  | PK                | Unique identifier                  |
| post_id     | FK → POST         | Which post this comment belongs to |
| user_id     | FK → USER         | Who left the comment               |
| category_id | FK → CATEGORY     | Comment category                   |
| body        | TEXT              | Comment text                       |
| created_at  | TIMESTAMPTZ       | Submission timestamp               |
| created_by  | INT · FK → USER   | Who created this comment           |
| updated_at  | TIMESTAMPTZ       | Last update timestamp              |
| updated_by  | INT · FK → USER   | Who last updated this comment      |

---

## 2. Relationships Between Entities

A **relationship** describes how two entities are connected. There are three types:

- **1:1** — One record links to exactly one other record
- **1:N** — One record links to many records
- **M:N** — Many records link to many records (requires a junction table)

---

## 3. Relationships Between Entities

| Relationship                              | Type | Description                                 |
| ----------------------------------------- | ---- | ------------------------------------------- |
| USER → POST                               | 1:N  | One user (author / admin) writes many posts |
| POST → CATEGORY                           | N:1  | Many posts belong to one category           |
| POST → COMMENT                            | 1:N  | One post has many comments                  |
| USER → COMMENT                            | 1:N  | One user leaves many comments               |
| COMMENT → CATEGORY                        | N:1  | Many comments belong to one category        |
| USER → USER (`created_by` / `updated_by`) | N:1  | Self-referencing audit trail on all tables  |

---

## 3. Entity Relationship Diagram — Retail Website Blog

```
┌───────────────────────────────────┐
│               USER                │
│───────────────────────────────────│
│ PK  user_id                       │
│     username                      │
│ UQ  email                         │
│     password_hash                 │
│     role  ENUM(admin, author)     │
│     created_at   TIMESTAMPTZ      │
│ FK  created_by   → USER           │
│     updated_at   TIMESTAMPTZ      │
│ FK  updated_by   → USER           │
└──────────────┬────────────────────┘
               │ 1
               │ writes
               │ N
               ▼
┌───────────────────────────────────┐       ┌──────────────────────────┐
│               POST                │  N    │        CATEGORY          │
│───────────────────────────────────│◄─────►│──────────────────────────│
│ PK  post_id                       │belongs│ PK  category_id          │
│ FK  user_id       → USER          │  to 1 │ UQ  name                 │
│ FK  category_id   → CATEGORY      │       │     created_at TIMESTAMPTZ│
│     title                         │       │ FK  created_by → USER    │
│     body                          │       │     updated_at TIMESTAMPTZ│
│     status ENUM(draft, published) │       │ FK  updated_by → USER    │
│     media_url                     │       └─────────────┬────────────┘
│     published_at  TIMESTAMPTZ     │                     │ 1
│     created_at    TIMESTAMPTZ     │                     │ categorizes
│ FK  created_by    → USER          │                     │ N
│     updated_at    TIMESTAMPTZ     │                     ▼
│ FK  updated_by    → USER          │       ┌──────────────────────────┐
└──────────────┬────────────────────┘  1    │        COMMENT           │
               │ has               ──────►  │──────────────────────────│
               │ N                          │ PK  comment_id           │
               └───────────────────────────►│ FK  post_id    → POST    │
                                            │ FK  user_id    → USER    │
                                            │ FK  category_id→ CATEGORY│
                                            │     body                 │
                                            │     created_at TIMESTAMPTZ│
                                            │ FK  created_by → USER    │
                                            │     updated_at TIMESTAMPTZ│
                                            │ FK  updated_by → USER    │
                                            └──────────────────────────┘
```

---

### Relationship Summary

```
              ┌──────────────────────────────┐
              │             USER             │
              │   role: ENUM(admin, author)  │
              │   email: UNIQUE              │
              └──────┬──────────────┬────────┘
                     │ 1            │ 1
                  writes          leaves
                     │ N            │ N
                     ▼              ▼
              ┌─────────────┐  ┌────────────────┐
              │    POST     │  │    COMMENT     │
              │  status:    │  │  category_id   │
              │  ENUM       │  │  (FK)          │
              │  (draft |   │  └───────┬────────┘
              │  published) │          │ N
              │  + media_url│    categorized by
              │             │          │ 1
              │             │          ▼
              └──────┬──────┘  ┌────────────────┐
                     │ N        │    CATEGORY    │
              belongs│to        │  name: UNIQUE  │
                     │ 1        └────────────────┘
                     └──────────────────►(same CATEGORY)
```

---

### Key Takeaways

- **4 core tables only**: USER, CATEGORY, POST, COMMENT — simplified from the original 9.
- The schema has **4 core tables**: USER, CATEGORY, POST, and COMMENT.
- **USER** supports two roles — `admin` and `author` — defined as an ENUM. Each user has a unique email address used for login.
- **CATEGORY** groups posts and comments under a named topic. The category name is unique across the system.
- **POST** is the central entity. It holds the blog content, publication status (`draft` or `published`), and an optional `media_url` for attaching an image or file.
- **COMMENT** belongs to both a post and a category, allowing comments to be organized by topic as well as by the post they respond to.
- Every table includes **full audit fields** — `created_at`, `created_by`, `updated_at`, and `updated_by` — to track who created and last modified each record.
- All relationships in the schema are **1:N** — one user writes many posts, one post has many comments, one category groups many posts and comments.
