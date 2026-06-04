# ADR-001: Consolidate to Flask Monolith (Remove Next.js)

**Status:** Accepted  
**Date:** 2024-06-04  
**Context:** Flask consolidation decision  
**Decision Maker:** Team

## Context

VibeDrive was originally architected as a two-framework monorepo:
- **Backend:** FastAPI (Python) for REST API
- **Frontend:** Next.js (React/TypeScript) for web UI

This dual-framework approach presented operational and maintenance challenges:

1. **Configuration Complexity:** Multiple config files (`.env`, `tsconfig.json`, `next.config.js`, `pyproject.toml`)
2. **Different Dev Environments:** Two package managers (pip, npm); two dev servers
3. **Build Processes:** Separate Docker images, deployments, and CI/CD logic
4. **Team Skills:** Python-focused team with limited frontend engineering resources
5. **Deployment Overhead:** Coordinating frontend+backend deployments; version misalignment risks

## Decision

Consolidate to a **Flask monolith** with Jinja2 templates for HTML rendering, removing Next.js entirely.

### Architecture Changes

**Before (FastAPI + Next.js):**
```
Frontend (React/TS)  ←→  API (FastAPI JSON) ←→  Database
(port 3000)              (port 8000)
```

**After (Flask):**
```
Flask App (port 5000)
├── HTML Routes (Jinja2 templates)
├── JSON API Routes
└── Database
```

### Technology Stack

| Aspect | Before | After |
|--------|--------|-------|
| Framework | FastAPI + Next.js | Flask only |
| Frontend | React/TypeScript SPA | Jinja2 templates + TailwindCSS |
| Styling | CSS/Tailwind | TailwindCSS (CDN) |
| Server | uvicorn + npm dev | Flask dev server + Gunicorn (prod) |
| Port | 8000 + 3000 | 5000 |
| Deployment | 2 Docker images | 1 Docker image |
| Config Files | .env, tsconfig.json, next.config.js, pyproject.toml | .env only |

### New Project Structure

```
app/
├── routes/
│   ├── api/         # JSON endpoints (/api/*)
│   │   ├── auth.py
│   │   └── skills.py
│   └── views/       # HTML routes (/)
│       ├── auth.py
│       └── dashboard.py
├── templates/       # Jinja2 HTML
├── static/          # CSS, JS, images
└── ...
```

## Consequences

### Positive ✅

1. **Unified Configuration:** Single `.env` file (with environment-specific overrides `.env.test`, `.env.uat`)
2. **Single Language:** Python across the entire application
3. **Simpler Deployment:** One Docker image, one CI/CD pipeline
4. **Faster Development:** No context-switching between frameworks
5. **Easier Onboarding:** New team members learn one framework
6. **Cleaner Monorepo:** No frontend/backend separation concerns

### Trade-offs ❌

1. **Frontend Interactivity:** Limited to server-rendered HTML + minimal JavaScript
   - ✅ **Mitigation:** TailwindCSS for styling; vanilla JS or HTMX/Alpine.js for interactions (future)
   - ✅ **Benefit:** No JavaScript dependency chains; simpler mental model

2. **Lost TypeScript:** Frontend loses type safety
   - ✅ **Mitigation:** Pydantic schemas enforce validation at API boundary

3. **No React SPAs:** Cannot build rich, single-page applications
   - ✅ **Scope Match:** VibeDrive's UI is dashboard + forms; traditional server-rendered works well

4. **Mobile Apps:** Harder to share code with React Native/Flutter
   - ✅ **Mitigation:** REST API remains; mobile apps can consume `/api/*` endpoints

5. **Separate Frontend Scaling:** Cannot independently scale frontend servers
   - ✅ **Trade-off:** Acceptable for current and near-term scale; monolith can be split later if needed

## Alternatives Considered

### 1. Keep FastAPI + Next.js (Rejected)
**Why rejected:** Operational overhead outweighs benefits for a small team. Configuration complexity grew with multi-environment deployments.

### 2. Switch to Django + Django Templates (Considered)
**Why rejected:** Django feels heavier and more opinionated than Flask. Team already understands FastAPI's async philosophy; Flask is a lighter transition.

### 3. Separate Frontend/Backend Repos (Considered)
**Why rejected:** Added orchestration complexity (separate CI/CD, versioning, deployment coordination). Monorepo advantages outweigh coordination overhead.

## Migration Path

1. ✅ Delete `frontend/` directory
2. ✅ Restructure `backend/src/` → `app/`
3. ✅ Separate API routes (`app/routes/api/`) from HTML routes (`app/routes/views/`)
4. ✅ Create Jinja2 templates in `app/templates/`
5. ✅ Update Dockerfile to remove Node.js
6. ✅ Update docker-compose and deployment configs
7. ⏳ Convert FastAPI routes to Flask (preserve business logic)
8. ⏳ Create HTML page templates
9. ⏳ Update tests and CI/CD

## Related Decisions

- [[adr-002-multi-environment-strategy]] — How to handle dev/test/uat/prod configs
- [[adr-003-separated-api-views]] — Why API and view routes are separate files

## Rollback Plan

If Flask consolidation proves problematic:
1. The API layer (`app/routes/api/`) is framework-agnostic; can be re-wrapped with FastAPI
2. HTML templates can be ported back to Next.js React components
3. **Estimated effort:** 2-3 weeks for full rollback

## Approval

- [ ] Team Lead
- [ ] Backend Lead
- [ ] DevOps Lead

---

**For questions:** See [docs/architecture.md](../architecture.md) for system design overview.
