# CMS API — Design & Testing Guide

---

## Base URL

```
http://localhost:8000
```

Interactive Swagger UI → http://localhost:8000/docs  
ReDoc UI → http://localhost:8000/redoc

---

## Authentication

> This version uses no auth token. `created_by` / `updated_by` are passed manually in the request body as the acting user's `user_id`. Auth middleware (JWT/OAuth2) can be layered on top in a future iteration.

---

## Global Response Codes

| Code | Meaning                        |
| ---- | ------------------------------ |
| 200  | OK — fetch / update success    |
| 201  | Created — resource created     |
| 204  | No Content — delete success    |
| 400  | Bad Request — validation error |
| 404  | Not Found — resource missing   |
| 422  | Unprocessable — schema error   |
| 500  | Internal Server Error          |

---

## 1. USER API `/users`

### POST `/users/` — Create a user

**Request Body**

```json
{
  "username": "manas_admin",
  "email": "manas@example.com",
  "password_hash": "hashed_password_string",
  "role": "admin",
  "created_by": null
}
```

**Response 201**

```json
{
  "user_id": 1,
  "username": "manas_admin",
  "email": "manas@example.com",
  "role": "admin",
  "created_at": "2026-02-25T10:00:00Z",
  "updated_at": "2026-02-25T10:00:00Z"
}
```

**Validation Rules**

- `email` must be a valid email format and unique
- `username` must not be blank
- `role` must be `admin` or `author` only

---

### GET `/users/` — List all users

**Response 200**

```json
[
  {
    "user_id": 1,
    "username": "manas_admin",
    "email": "manas@example.com",
    "role": "admin",
    "created_at": "2026-02-25T10:00:00Z",
    "updated_at": "2026-02-25T10:00:00Z"
  }
]
```

---

### GET `/users/{user_id}` — Get one user

```
GET /users/1
```

**Response 200** — same as single user object above  
**Response 404** — `{ "detail": "User not found" }`

---

### PATCH `/users/{user_id}` — Update a user

```
PATCH /users/1
```

**Request Body** (all fields optional)

```json
{
  "username": "manas_updated",
  "role": "author",
  "updated_by": 1
}
```

**Response 200** — updated user object

---

### DELETE `/users/{user_id}` — Delete a user

```
DELETE /users/1
```

**Response 204** — no body  
**Response 404** — `{ "detail": "User not found" }`

---

## 2. CATEGORY API `/categories`

### POST `/categories/` — Create a category

**Request Body**

```json
{
  "name": "Skincare Tips",
  "created_by": 1
}
```

**Response 201**

```json
{
  "category_id": 1,
  "name": "Skincare Tips",
  "created_at": "2026-02-25T10:00:00Z",
  "updated_at": "2026-02-25T10:00:00Z"
}
```

**Validation Rules**

- `name` must not be blank and must be unique

---

### GET `/categories/` — List all categories

**Response 200** — array of category objects

---

### GET `/categories/{category_id}` — Get one category

```
GET /categories/1
```

---

### PATCH `/categories/{category_id}` — Update a category

```json
{
  "name": "Hair Care",
  "updated_by": 1
}
```

---

### DELETE `/categories/{category_id}` — Delete a category

```
DELETE /categories/1
```

---

## 3. POST API `/posts`

### POST `/posts/` — Create a post

**Request Body**

```json
{
  "user_id": 1,
  "category_id": 1,
  "title": "Top 5 Skincare Routines",
  "body": "Here are the top 5 routines recommended by dermatologists...",
  "status": "draft",
  "media_url": "https://cdn.example.com/images/skincare.jpg",
  "created_by": 1
}
```

**Response 201**

```json
{
  "post_id": 1,
  "user_id": 1,
  "category_id": 1,
  "title": "Top 5 Skincare Routines",
  "body": "Here are the top 5 routines...",
  "status": "draft",
  "media_url": "https://cdn.example.com/images/skincare.jpg",
  "published_at": null,
  "created_at": "2026-02-25T10:00:00Z",
  "updated_at": "2026-02-25T10:00:00Z"
}
```

**Validation Rules**

- `title` and `body` must not be blank
- `status` must be `draft` or `published`
- `published_at` is auto-set when status is set to `published`
- `user_id` and `category_id` must reference existing records

---

### GET `/posts/` — List all posts

```
GET /posts/             → all posts
GET /posts/?status=draft       → drafts only
GET /posts/?status=published   → published only
```

---

### GET `/posts/{post_id}` — Get one post

```
GET /posts/1
```

---

### PATCH `/posts/{post_id}` — Update / Publish a post

```
PATCH /posts/1
```

**Request Body** (all fields optional)

```json
{
  "status": "published",
  "title": "Updated Title",
  "updated_by": 1
}
```

> Setting `status` to `published` automatically stamps `published_at` with the current timestamp.

---

### DELETE `/posts/{post_id}` — Delete a post

```
DELETE /posts/1
```

> Deleting a post also deletes all its comments (CASCADE).

---

## 4. COMMENT API `/comments`

### POST `/comments/` — Create a comment

**Request Body**

```json
{
  "post_id": 1,
  "user_id": 1,
  "category_id": 1,
  "body": "Really helpful post, thanks!",
  "created_by": 1
}
```

**Response 201**

```json
{
  "comment_id": 1,
  "post_id": 1,
  "user_id": 1,
  "category_id": 1,
  "body": "Really helpful post, thanks!",
  "created_at": "2026-02-25T10:00:00Z",
  "updated_at": "2026-02-25T10:00:00Z"
}
```

---

### GET `/comments/` — List comments

```
GET /comments/               → all comments
GET /comments/?post_id=1     → comments for post 1 only
```

---

### GET `/comments/{comment_id}` — Get one comment

```
GET /comments/1
```

---

### PATCH `/comments/{comment_id}` — Update a comment

```json
{
  "body": "Updated comment text",
  "updated_by": 1
}
```

---

### DELETE `/comments/{comment_id}` — Delete a comment

```
DELETE /comments/1
```

---

## Testing Guide

### Option A — Swagger UI (Recommended for beginners)

1. Start the server: `uvicorn main:app --reload --port 8000`
2. Open **http://localhost:8000/docs**
3. Click any endpoint → click **"Try it out"** → fill in the body → click **"Execute"**
4. Response appears directly on screen with status code

---

### Option B — cURL (Terminal)

**Create a user**

```bash
curl -X POST http://localhost:8000/users/ \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"manas\",\"email\":\"manas@example.com\",\"password_hash\":\"abc123\",\"role\":\"admin\"}"
```

**Get all users**

```bash
curl http://localhost:8000/users/
```

**Create a category**

```bash
curl -X POST http://localhost:8000/categories/ \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Skincare Tips\",\"created_by\":1}"
```

**Create a post**

```bash
curl -X POST http://localhost:8000/posts/ \
  -H "Content-Type: application/json" \
  -d "{\"user_id\":1,\"category_id\":1,\"title\":\"My First Post\",\"body\":\"Post content here\",\"status\":\"draft\",\"created_by\":1}"
```

**Publish a post**

```bash
curl -X PATCH http://localhost:8000/posts/1 \
  -H "Content-Type: application/json" \
  -d "{\"status\":\"published\",\"updated_by\":1}"
```

**Get published posts only**

```bash
curl http://localhost:8000/posts/?status=published
```

**Add a comment**

```bash
curl -X POST http://localhost:8000/comments/ \
  -H "Content-Type: application/json" \
  -d "{\"post_id\":1,\"user_id\":1,\"category_id\":1,\"body\":\"Great post!\",\"created_by\":1}"
```

**Get all comments for a post**

```bash
curl http://localhost:8000/comments/?post_id=1
```

**Delete a post (cascades comments)**

```bash
curl -X DELETE http://localhost:8000/posts/1
```

---

### Option C — Postman

1. Download Postman from https://www.postman.com/downloads/
2. Create a new Collection called **CMS API**
3. For each endpoint add a request:
   - Set method (GET / POST / PATCH / DELETE)
   - Set URL e.g. `http://localhost:8000/users/`
   - For POST/PATCH: go to **Body → raw → JSON** and paste the request body
4. Click **Send**

**Recommended test order in Postman:**

```
1. POST /users/          → create admin user       (get user_id)
2. POST /categories/     → create category         (get category_id)
3. POST /posts/          → create post as draft     (get post_id)
4. PATCH /posts/1        → publish the post
5. POST /comments/       → add comment to post
6. GET /comments/?post_id=1  → verify comment appears
7. DELETE /comments/1    → delete comment
8. DELETE /posts/1       → delete post + its comments
```

---

## Relationship Test Scenarios

| Scenario                               | What to verify                              |
| -------------------------------------- | ------------------------------------------- |
| Create post with invalid `user_id`     | Returns 500 FK violation                    |
| Create post with invalid `category_id` | Returns 500 FK violation                    |
| Delete a post                          | All its comments are also deleted (CASCADE) |
| Create user with duplicate email       | Returns 500 unique violation                |
| Create category with duplicate name    | Returns 500 unique violation                |
| Set post status to `published`         | `published_at` is auto-populated            |
| PATCH with no fields                   | Returns 400 "No fields to update"           |
