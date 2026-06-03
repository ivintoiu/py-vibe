# API Documentation

## Overview

VibeDrive API is a RESTful service built with FastAPI, providing endpoints for skill management, learning paths, and progress tracking.

**Base URL:** `http://localhost:8000` (development)

## Authentication

All protected endpoints require a JWT Bearer token in the `Authorization` header:

```
Authorization: Bearer <jwt_token>
```

### Obtain Token
```http
POST /api/auth/token
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "password123"
}
```

Response:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

## Endpoints (Planned)

### Skills

#### Create Skill
```http
POST /api/skills
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Python",
  "description": "Learn Python programming",
  "difficulty_level": 2,
  "estimated_hours": 50
}
```

#### List Skills
```http
GET /api/skills?skip=0&limit=10
Authorization: Bearer <token>
```

#### Get Skill
```http
GET /api/skills/{skill_id}
Authorization: Bearer <token>
```

#### Update Skill
```http
PATCH /api/skills/{skill_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "status": "learning"
}
```

#### Delete Skill
```http
DELETE /api/skills/{skill_id}
Authorization: Bearer <token>
```

### Learning Paths (Planned)

- `POST /api/learning-paths` — Generate learning path
- `GET /api/learning-paths/{path_id}` — Get learning path
- `GET /api/learning-paths/{path_id}/milestones` — Get milestones

### Study Plans (Planned)

- `GET /api/study-plans/current` — Get current week's study plan
- `GET /api/study-plans/history` — Get past study plans

### Resources (Planned)

- `GET /api/resources/search` — Search learning resources
- `POST /api/resources/like` — Save resource to favorites

## Response Format

All responses are JSON with consistent structure:

```json
{
  "status": "success",
  "data": { /* response payload */ },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

Errors:
```json
{
  "status": "error",
  "message": "Error description",
  "code": "SKILL_NOT_FOUND"
}
```

## Status Codes

| Code | Meaning |
|---|---|
| 200 | Success |
| 201 | Created |
| 204 | No Content (success, no body) |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 422 | Unprocessable Entity (validation error) |
| 500 | Internal Server Error |

## Rate Limiting

API endpoints are rate-limited. Check response headers:
- `X-RateLimit-Limit` — requests per window
- `X-RateLimit-Remaining` — remaining requests
- `X-RateLimit-Reset` — reset timestamp

## WebSocket (Planned)

Real-time progress updates:

```
ws://localhost:8000/ws/progress/{skill_id}
```

Messages:
```json
{
  "event": "milestone_completed",
  "skill_id": 1,
  "milestone_id": 5,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## OpenAPI/Swagger

Interactive API docs available at: http://localhost:8000/docs
