# PY-VIBE: Order History API

❗ This repository is a personal exercise of Vibe and Agent Coding. The project does not have any value. It is just a flow state, some LLM magic, and a vision that came together one prompt at a time. The code reflects a moment in time where the logic felt right, the prompts were hitting, and the aesthetic mattered as much as the execution.
* Logic Style: Intuitive and emergent.
* Dev Stack: Python + Pure Inspiration.
* Vibe Check: Passed.

## Features

A Python REST API built with **FastAPI** and **asyncpg** that lets authenticated users retrieve their own paginated order history from a PostgreSQL database.

- **JWT authentication** — issue tokens via `POST /auth/token`
- **Ownership enforcement** — users can only access their own orders (403 otherwise)
- **Paginated results** — 10 orders per page, sorted by `created_at DESC`
- **Async throughout** — asyncpg connection pool, fully non-blocking
- **Auto docs** — OpenAPI UI at `/docs`, ReDoc at `/redoc`

---

## Architecture

```mermaid
flowchart TD
    Client(["Client"])

    subgraph API ["API Layer (main.py)"]
        Token["POST /auth/token"]
        Orders["GET /users/{user_id}/orders"]
        EH["Exception Handler\n503 on unhandled errors"]
    end

    subgraph Auth ["Auth (auth.py)"]
        AuthUser["authenticate_user()\nfetch user + bcrypt verify"]
        CreateToken["create_access_token()\nsign JWT"]
        GetUser["get_current_user()\ndecode + validate JWT"]
        OwnerGuard["verify_ownership()\ncaller == user_id → 403"]
    end

    subgraph Svc ["Order Service (services.py)"]
        GetOrders["get_orders_for_user()\npaginate + 404 guard"]
    end

    subgraph Repo ["Repository (repository.py)"]
        FetchByUsername["fetch_user_by_username()"]
        FetchById["fetch_user_by_id()"]
        FetchOrders["fetch_orders_by_user_id()\nLIMIT / OFFSET + COUNT OVER()"]
    end

    subgraph Infra ["Infrastructure"]
        Pool["asyncpg Connection Pool\n(database.py)\nmin=2 max=10"]
        Config["Settings\n(config.py)\nDATABASE_URL · JWT_SECRET"]
        Logger["Structured Logger\n(logger.py)\n→ py-vibe.log"]
        DB[("PostgreSQL\nusers · orders")]
    end

    Client -->|"POST credentials"| Token
    Client -->|"GET + Bearer JWT"| Orders

    Token --> AuthUser
    AuthUser --> FetchByUsername
    AuthUser --> CreateToken
    CreateToken -->|"JWT"| Client

    Orders --> GetUser
    GetUser -->|"401 invalid token"| Client
    Orders --> OwnerGuard
    OwnerGuard -->|"403 wrong user"| Client
    Orders --> GetOrders
    GetOrders --> FetchById
    GetOrders --> FetchOrders
    GetOrders -->|"PaginatedOrderResponse"| Client
    GetOrders -->|"404 user not found"| Client

    FetchByUsername --> Pool
    FetchById --> Pool
    FetchOrders --> Pool
    Pool <-->|"asyncpg"| DB

    Config -.->|"DSN"| Pool
    Config -.->|"JWT_SECRET"| Auth
    Logger -.->|"log calls"| API
    Logger -.->|"log calls"| Auth
    Logger -.->|"log calls"| Svc
    Logger -.->|"log calls"| Infra
    EH -.->|"catches all"| API
```

---

## Project Structure

```
py-vibe/
├── main.py              # API Layer — route handlers, app lifecycle
├── auth.py              # Auth Middleware, Authorization Guard, Token Service helpers
├── services.py          # Order Service — business logic + pagination
├── repository.py        # Database Layer — all parameterized SQL queries
├── database.py          # Connection Pool — asyncpg pool init/teardown
├── schemas.py           # Pydantic Schemas — request/response models
├── config.py            # Configuration — env vars via pydantic-settings
├── logger.py            # Structured logging setup
├── schema.sql           # PostgreSQL table definitions
├── seed.py              # Dev fixtures (alice + bob)
├── docker-compose.yml   # Local PostgreSQL via Docker
├── pyproject.toml       # Dependencies + tool config
└── .env.example
```

---

## Setup

### 1. Start the database

```bash
docker compose up -d
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env with your DATABASE_URL and a strong JWT_SECRET
```

### 4. Seed dev data (optional)

```bash
python seed.py
# Creates: alice / password123  and  bob / password456
```

### 5. Run the server

```bash
uvicorn main:app --reload
```

---

## API Usage

### Obtain a token

```bash
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "secret"}'
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

---

### Fetch order history

```bash
curl http://localhost:8000/users/1/orders?page=1 \
  -H "Authorization: Bearer eyJ..."
```

**Response:**
```json
{
  "orders": [
    {
      "id": 99,
      "user_id": 1,
      "status": "delivered",
      "total_amount": "49.99",
      "created_at": "2024-03-15T10:30:00Z",
      "items": [{"product_id": 7, "name": "Widget", "qty": 1, "unit_price": "49.99"}]
    }
  ],
  "page": 1,
  "page_size": 10,
  "total": 1,
  "total_pages": 1
}
```

---

## HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200  | Success |
| 401  | Missing, expired, or invalid JWT |
| 403  | Authenticated but accessing another user's orders |
| 404  | User not found |
| 422  | Invalid `user_id` or `page` parameter |
| 503  | Database or server error |

---

## Storing Passwords

To create a bcrypt hash for a user's password (for seeding the DB):

```python
import bcrypt
hashed = bcrypt.hashpw(b"secret", bcrypt.gensalt()).decode("utf-8")
print(hashed)
```