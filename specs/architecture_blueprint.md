# **VibeDrive — Full Architecture Blueprint**

---

## **1. Concept Overview**

**VibeDrive** is a personal learning planner that helps users:
- Define skills they want to learn
- Break them into milestones
- Track progress visually
- Receive weekly AI‑generated study plans
- Get curated resources (videos, articles, exercises)
- Maintain motivation through streaks, reminders, and insights

It’s designed for **students, professionals, and self‑learners**.

---

## **2. Core Features**

- **Skill definition & hierarchy**
  Users define skills → subskills → milestones.

- **Learning path generator**
  LLM creates a structured roadmap based on user goals.

- **Weekly AI study plan**
  Automatically generated every Sunday morning.

- **Resource discovery**
  Uses embeddings to find relevant content from curated datasets.

- **Progress tracking dashboard**
  Charts, streaks, completion percentages.

- **Notifications**
  Email or push reminders for study sessions.

- **Gamification**
  XP, badges, streaks, leveling.

- **Multi‑device UI**
  Desktop + mobile‑friendly.

---

## **3. Architecture Overview**

### **Languages & Frameworks**
- **Backend:** Python, Flask (synchronous monolith)
- **Database:** PostgreSQL with psycopg2 DBAPI (raw SQL, ThreadedConnectionPool)
- **Frontend:** Jinja2 templates, TailwindCSS + vanilla JS
- **AI Layer:** LangChain, OpenAI/Local LLMs
- **Vector Search:** Qdrant
- **Task Scheduling:** Celery + Redis
- **Auth:** JWT (python-jose) + bcrypt

---

### **Architectural Patterns**
- **Hexagonal architecture** for clean separation
- **CQRS** for read/write separation (optional but educational)
- **Repository pattern** for data access
- **Dependency Injection** using FastAPI’s DI system
- **Event‑driven modules** for notifications and weekly plan generation

---

### **API Strategy**
- **REST** for core CRUD
- **GraphQL** for flexible UI queries
- **WebSockets** for real‑time progress updates

---

### **Storage Strategy**
- **PostgreSQL** for relational data
- **Redis** for caching & background jobs
- **Qdrant** for embeddings
- **S3/MinIO** for resource metadata or user uploads

---

### **Infrastructure Stack**
- **Containers:** Docker
- **Orchestration:** Kubernetes (optional for later)
- **IaC:** Terraform modules for DB, buckets, compute
- **GitOps:** ArgoCD for deployment
- **CI/CD:** GitHub Actions
- **Observability:**
  - Prometheus
  - Grafana
  - OpenTelemetry traces

---

### **Security Model**
- **OAuth2 login** (Google, GitHub)
- **JWT access tokens**
- **Role‑based permissions** (admin/user)
- **Vault** for secrets
- **HTTPS everywhere**
- **Rate limiting** via Traefik or NGINX

---

## **4. AI Integration**

### **AI‑Native Components**
- **Learning Path Generator**
  LLM takes user goals → outputs structured JSON roadmap.

- **Weekly Study Plan Agent**
  Runs every Sunday → analyzes progress → generates plan.

- **Resource Embedding Search**
  Embeds curated resources → matches to user skills.

- **Reflection Insights**
  “You improved 12% this week; focus on X next.”

### **Agent Workflow Example**
1. User defines a skill
2. Agent generates milestones
3. Agent fetches resources
4. Agent schedules weekly tasks
5. Agent monitors progress
6. Agent adjusts plan dynamically

---

## **5. Extensibility & Open‑Source Potential**

### **Plugin System**
- **Skill Packs**
  Python, Cloud, DevOps, AI, Languages, Math.

- **Resource Providers**
  YouTube, Coursera, GitHub repos, Medium articles.

- **AI Model Adapters**
  OpenAI, Anthropic, Llama, Mistral, Local models.

- **Gamification Modules**
  Custom badges, XP rules, streak logic.

### **Community Contributions**
- New learning templates
- New dashboards
- Mobile app
- Browser extension for “Save to VibeDrive”

---

## **6. Difficulty & Impact Rating**
- **Difficulty:** 5/10
  (Approachable but teaches many modern concepts)
- **Impact:** 8/10
  (Useful for anyone learning anything)

---

## **7. Real‑Life Utility**
- Students planning study schedules
- Professionals learning cloud, AI, programming
- People preparing for certifications
- Anyone wanting structured self‑improvement

---

## Related Reading

- [Project Context](../CLAUDE.md) — Implementation notes and design decisions
- [psycopg2 Documentation](https://www.psycopg.org/docs/)
- [Flask Documentation](https://flask.palletsprojects.com/en/stable/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
