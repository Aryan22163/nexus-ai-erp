# NEXUS AI: Production Deployment & Infrastructure Specification

## 1. Deployment Topology

The NEXUS AI platform is containerized for seamless local development and cloud production deployment (AWS, GCP, DigitalOcean, or Bare-metal Kubernetes).

```
                            INTERNET
                                │
                                ▼
                   ┌─────────────────────────┐
                   │   Cloudflare / Edge CDN │
                   └────────────┬────────────┘
                                │ HTTPS (Port 443)
                                ▼
                   ┌─────────────────────────┐
                   │    Reverse Proxy NGINX  │
                   │  - SSL Termination      │
                   │  - Gzip / Brotli        │
                   │  - Rate Limiting        │
                   └────────────┬────────────┘
                                │
        ┌───────────────────────┴───────────────────────┐
        │ /api/*, /ws, /docs                            │ /* (UI Pages)
        ▼                                               ▼
┌───────────────────────────────┐               ┌───────────────────────────────┐
│     FastAPI Backend (x2+)     │               │     Next.js Frontend (x2+)    │
│  - Port 8000                  │               │  - Port 3000                  │
│  - Uvicorn Workers            │               │  - Node.js Standalone Build   │
└───────────────┬───────────────┘               └───────────────────────────────┘
                │
                ├───────────────────────────────┐
                ▼                               ▼
┌───────────────────────────────┐       ┌───────────────────────────────┐
│     PostgreSQL + pgvector     │       │         Redis Cluster         │
│  - Primary DB                 │       │  - Cache & Session Store      │
│  - Persistent Volume Mount    │       │  - Background Job Message Bus │
└───────────────▲───────────────┘       └───────────────▲───────────────┘
                │                                       │
                └───────────────────────┬───────────────┘
                                        │
                        ┌───────────────┴───────────────┐
                        │      Background Worker        │
                        │  - Celery / ARQ               │
                        │  - Scheduled ML Inferences    │
                        │  - Vector Embedding Queue     │
                        └───────────────────────────────┘
```

---

## 2. Docker Compose Services Specification

### 2.1 Core Services in `docker-compose.yml`

| Service Name | Image / Base | Internal Port | Description |
|---|---|---|---|
| `postgres` | `pgvector/pgvector:pg16` | 5432 | Primary database with vector indexing extensions |
| `redis` | `redis:7.2-alpine` | 6379 | In-memory cache, rate limiter, and task broker |
| `backend` | Python 3.12 (FastAPI) | 8000 | Core REST API, SSE streams, and WebSocket hub |
| `worker` | Python 3.12 (Celery/ARQ) | N/A | Asynchronous task execution & scheduled jobs |
| `frontend` | Node.js 20 (Next.js 14) | 3000 | Production UI frontend |
| `nginx` | `nginx:alpine` | 80, 443 | Gateway reverse proxy and static asset cache |

---

## 3. Environment Variables Strategy

Environment variables are partitioned into clear categories in `.env.example`:
- **Application & Server**: `ENVIRONMENT`, `DEBUG`, `SECRET_KEY`, `CORS_ORIGINS`.
- **Database & Persistence**: `DATABASE_URL`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`.
- **Redis & Queues**: `REDIS_URL`.
- **Authentication**: `JWT_SECRET`, `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`.
- **AI & LLM Services**: `DEFAULT_LLM_PROVIDER`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `LOCAL_LLM_BASE_URL`.
- **Storage**: `STORAGE_BACKEND` (`local` or `s3`), `STORAGE_PATH`, `S3_BUCKET`, `S3_ACCESS_KEY`.
- **Email / SMTP**: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `EMAILS_FROM_EMAIL`.

> [!CAUTION]
> Production secrets must never be committed to Git. All secrets in staging and production environments must be loaded via Secret Managers (AWS Secrets Manager, HashiCorp Vault, or GitHub Secrets).

---

## 4. Production Hardening Checklist

- [x] **Non-Root Execution**: Dockerfiles run services under dedicated unprivileged `appuser` accounts.
- [x] **Read-Only Database Pool**: AI ad-hoc queries execute on a strictly read-only database role without write or schema mutation privileges.
- [x] **Rate Limiting**: NGINX limits IP requests to 30 req/sec for general APIs and 5 req/min for authentication endpoints.
- [x] **CORS & CSP**: Restrictive Cross-Origin Resource Sharing headers and strict Content Security Policies.
- [x] **Health Check Probes**: Liveness (`/health/live`) and readiness (`/health/ready`) endpoints on backend and frontend containers.
- [x] **Volume Backup**: Automated PostgreSQL `pg_dump` snapshotting with retention policies.
