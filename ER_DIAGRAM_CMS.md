# CMS Entities & Relationships — Retail Website Blog

---

## 1. Research: Entities in a Content Management System

An **entity** in a CMS is any distinct object or concept that needs to be stored and managed. Below are the core entities found across most CMS platforms, along with their typical attributes.

---

### USER

Represents anyone who interacts with the CMS backend — authors, editors, admins.

| Attribute     | Description                          |
| ------------- | ------------------------------------ |
| user_id       | Unique identifier (Primary Key)      |
| username      | Display name                         |
| email         | Login email                          |
| password_hash | Encrypted password                   |
| role          | admin / editor / author / subscriber |
| created_at    | Account creation date                |

---

### POST

The central entity — a blog article or piece of content.

| Attribute    | Description                                           |
| ------------ | ----------------------------------------------------- |
| post_id      | Unique identifier (Primary Key)                       |
| user_id      | Who wrote it (Foreign Key → USER)                     |
| category_id  | Which category it belongs to (Foreign Key → CATEGORY) |
| title        | Post headline                                         |
| body         | Main content (rich text)                              |
| slug         | URL-friendly version of title                         |
| status       | draft / published / archived                          |
| published_at | Publication timestamp                                 |

---

### CATEGORY

Organizes posts into broad topics (e.g., "Shoes", "Skincare Tips").

| Attribute   | Description                     |
| ----------- | ------------------------------- |
| category_id | Unique identifier (Primary Key) |
| name        | Category label                  |
| slug        | URL-friendly name               |
| description | Short summary                   |

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

Reader responses on a published post.

| Attribute  | Description                                   |
| ---------- | --------------------------------------------- |
| comment_id | Unique identifier (Primary Key)               |
| post_id    | Which post it belongs to (Foreign Key → POST) |
| user_id    | Who left the comment (Foreign Key → USER)     |
| body       | Comment text                                  |
| status     | pending / approved / spam                     |
| created_at | Submission timestamp                          |

---

### MEDIA

Images, videos, or files uploaded and used within posts.

| Attribute | Description                     |
| --------- | ------------------------------- |
| media_id  | Unique identifier (Primary Key) |
| user_id   | Uploader (Foreign Key → USER)   |
| file_url  | Public URL of the file          |
| type      | image / video / pdf             |
| alt_text  | Accessibility description       |

---

### PRODUCT _(Retail-specific)_

A product from the store that can be referenced/featured inside blog posts.

| Attribute     | Description                     |
| ------------- | ------------------------------- |
| product_id    | Unique identifier (Primary Key) |
| name          | Product name                    |
| price         | Product price                   |
| sku           | Stock keeping unit              |
| thumbnail_url | Product image                   |
| product_url   | Link to the product page        |

---

## 2. Relationships Between Entities

A **relationship** describes how two entities are connected. There are three types:

- **1:1** — One record links to exactly one other record
- **1:N** — One record links to many records
- **M:N** — Many records link to many records (requires a junction table)

---

| Relationship    | Type | Description                                                          |
| --------------- | ---- | -------------------------------------------------------------------- |
| USER → POST     | 1:N  | One user writes many posts                                           |
| POST → CATEGORY | N:1  | Many posts belong to one category                                    |
| POST ↔ TAG      | M:N  | A post has many tags; a tag applies to many posts                    |
| POST → COMMENT  | 1:N  | One post has many comments                                           |
| USER → COMMENT  | 1:N  | One user leaves many comments                                        |
| USER → MEDIA    | 1:N  | One user uploads many media files                                    |
| POST ↔ PRODUCT  | M:N  | A post can feature many products; a product can appear in many posts |

> M:N relationships are resolved using **junction tables**: `POST_TAG` and `POST_PRODUCT`.

---

## 3. Entity Relationship Diagram — Retail Website Blog

```
┌─────────────────────┐          ┌─────────────────────┐
│        USER         │          │      CATEGORY       │
│─────────────────────│          │─────────────────────│
│ PK  user_id         │          │ PK  category_id     │
│     username        │          │     name            │
│     email           │          │     slug            │
│     role            │          └──────────┬──────────┘
└────────┬────────────┘                     │ 1
         │ 1                                │
         │                                  │ belongs to
  writes │                                  │
         │ N                                │ N
         ▼                                  ▼
┌─────────────────────────────────────────────────────┐
│                        POST                         │
│─────────────────────────────────────────────────────│
│ PK  post_id                                         │
│ FK  user_id                                         │
│ FK  category_id                                     │
│     title  │  body  │  slug  │  status  │  published_at │
└──────┬──────────────────────┬───────────────────────┘
       │ 1                    │ 1
       │                      │
  has  │              features│
       │ N                    │ N (via POST_PRODUCT)
       ▼                      ▼
┌──────────────────┐   ┌─────────────────────┐
│     COMMENT      │   │      PRODUCT        │
│──────────────────│   │─────────────────────│
│ PK  comment_id   │   │ PK  product_id      │
│ FK  post_id      │   │     name            │
│ FK  user_id      │   │     price           │
│     body         │   │     sku             │
│     status       │   │     thumbnail_url   │
└──────────────────┘   └─────────────────────┘


POST ◄──────────────────────────────► TAG
      M  (via POST_TAG junction)   N
      │                             │
      │  POST_TAG                   │
      │  ┌────────────┐             │
      └─►│  post_id   │◄────────────┘
         │  tag_id    │
         └────────────┘


USER ──────────────────────────────► MEDIA
  1    uploads                     N
```

---

### Relationship Summary

```
USER  ──(writes)──►  POST  ──(belongs to)──►  CATEGORY
 │                    │
 │(leaves)            │(has)         (tagged with)
 ▼                    ▼           POST ◄────────► TAG
COMMENT ◄──(on)── POST           (via POST_TAG)
                    │
                    │(features)
                    ▼
                 PRODUCT
              (via POST_PRODUCT)
```

---

### Key Takeaways

- **POST is the central entity** — everything connects to it.
- **USER has two roles**: as an author (writes posts) and as a reader (leaves comments).
- **CATEGORY** is a strict 1:N grouping; **TAG** is a flexible M:N labelling system.
- **PRODUCT** is the retail-specific addition — it links blog content to the store catalogue.
- **Junction tables** (`POST_TAG`, `POST_PRODUCT`) resolve M:N relationships cleanly.

```

```
