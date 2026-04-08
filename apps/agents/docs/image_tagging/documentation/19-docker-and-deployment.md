# 19 — Docker and Deployment

This document describes the backend and frontend Dockerfiles, docker-compose.yml (services, ports, env, volumes), .dockerignore usage, build and run commands, and production considerations (NEXT_PUBLIC_API_URL).

---

## docker-compose.yml

**Location:** Project root.

```yaml
services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - backend_uploads:/app/uploads
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        NEXT_PUBLIC_API_URL: http://localhost:8000
    ports:
      - "3000:3000"
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  backend_uploads:
```

- **backend:** Builds from backend/Dockerfile; exposes 8000; loads .env from project root; mounts named volume backend_uploads to /app/uploads so uploaded images persist across restarts.
- **frontend:** Builds from frontend/Dockerfile; build-arg NEXT_PUBLIC_API_URL is baked into the client bundle (default http://localhost:8000); exposes 3000; depends_on backend for startup order.
- **.env** at project root must contain OPENAI_API_KEY; optionally DATABASE_URI for Supabase.

---

## Backend Dockerfile

**Location:** backend/Dockerfile.

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
RUN mkdir -p uploads

EXPOSE 8000

CMD ["uvicorn", "src.server:app", "--host", "0.0.0.0", "--port", "8000"]
```

- Base: python:3.11-slim. Dependencies from requirements.txt. Application code in src/. uploads directory created. Server runs with uvicorn on 0.0.0.0:8000 so it is reachable from the host. Project root .env is not copied into the image; it is provided via env_file in compose (or -e at run time). DATABASE_URI and OPENAI_API_KEY should be set in .env or environment.

---

## Frontend Dockerfile

**Location:** frontend/Dockerfile.

**Stage 1 — builder:**

- Base: node:20-alpine. WORKDIR /app. COPY package.json and lockfile; npm ci. COPY . . (full frontend tree). ARG NEXT_PUBLIC_API_URL=http://localhost:8000, ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL. npm run build (produces .next/standalone and .next/static for standalone output).

**Stage 2 — runner:**

- Base: node:20-alpine. NODE_ENV=production, NEXT_TELEMETRY_DISABLED=1. Non-root user nextjs (uid 1001). COPY from builder: public, .next/standalone, .next/static. USER nextjs. EXPOSE 3000. CMD ["node", "server.js"].

- Next.js standalone output is used so the runner image does not need npm or the full source. The API URL is fixed at build time via NEXT_PUBLIC_API_URL.

---

## .dockerignore

- **backend:** Typically ignore __pycache__, .env, .git, etc., so only requirements.txt and src/ are copied. Keeps image small and avoids leaking .env into image if not intended.
- **frontend:** Ignore node_modules, .next (from host), .git, etc., so npm ci and build run in a clean context.

---

## Build and run commands

**From project root:**

```bash
docker compose up --build
```

- Builds backend and frontend (with NEXT_PUBLIC_API_URL=http://localhost:8000 by default), starts both services. App at http://localhost:3000, API at http://localhost:8000.

**Build only:**

```bash
docker compose build
```

**Run in background:**

```bash
docker compose up -d --build
```

**Stop:**

```bash
docker compose down
```

---

## Production: NEXT_PUBLIC_API_URL

- In production, the browser must call the real API URL (e.g. https://api.example.com). Set NEXT_PUBLIC_API_URL at **build time** when building the frontend image, e.g.:

  ```yaml
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        NEXT_PUBLIC_API_URL: https://api.yourdomain.com
  ```

- Or pass build-arg in CLI: `docker compose build --build-arg NEXT_PUBLIC_API_URL=https://api.yourdomain.com frontend`. Then run the stack with the same image. Backend must be deployed separately (or in the same compose with correct ports and env); CORS must allow the frontend origin.

---

## Pushing to a registry

- Tag images: `docker tag image-analysis-agent-backend your-registry/image-analysis-agent-backend:tag`, same for frontend. Push: `docker push your-registry/image-analysis-agent-backend:tag`. On the deployment host, use these image names in compose or orchestrator and set env_file or environment variables (OPENAI_API_KEY, DATABASE_URI) as appropriate.
