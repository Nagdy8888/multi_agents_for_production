# Phase 0: Project Skeleton and Configuration — Setup Guide

## What This Phase Adds

- Backend folder with FastAPI app, health check, CORS, and image_tagging agent package stubs
- Frontend Next.js app with App Router, Tailwind, shadcn/ui, theme toggle, and Navbar
- Docker: Dockerfiles and docker-compose for running backend and frontend in containers
- Documentation folder tree and initial PROGRESS diagram
- README in every code folder

## Prerequisites

- Docker and Docker Compose
- Project root `.env` with at least `OPENAI_API_KEY` (required for later phases)

## Files Changed


| Path                                                                                    | Change                        |
| --------------------------------------------------------------------------------------- | ----------------------------- |
| `backend/requirements.txt`, `backend/Dockerfile`, `backend/.dockerignore`               | Added                         |
| `backend/uploads/.gitkeep`                                                              | Added                         |
| `backend/src/*.py`, `backend/src/**/__init__.py`, placeholders                          | Added                         |
| `backend/src/image_tagging/settings.py`                                                 | Added                         |
| `backend/src/server.py`                                                                 | Added                         |
| `frontend/`                                                                             | Created via create-next-app   |
| `frontend/Dockerfile`, `frontend/.dockerignore`, `frontend/next.config.ts` (standalone) | Added                         |
| `frontend/.env.local`                                                                   | Added (for local dev only)    |
| `frontend/src/components/ThemeProvider.tsx`, `ThemeToggle.tsx`, `Navbar.tsx`            | Added                         |
| `frontend/src/app/layout.tsx`, `page.tsx`, `frontend/src/app/search/page.tsx`           | Modified/added                |
| `docker-compose.yml`                                                                    | Added                         |
| `docs/**`                                                                               | READMEs and PROGRESS.md added |
| `backend/README.md`, `backend/src/README.md`, etc.                                      | Added                         |


## Step-by-Step Setup (Docker)

### 1. Run with Docker

From the project root:

```bash
docker compose up --build
```

- **Frontend:** [http://localhost:3000](http://localhost:3000)  
- **Backend API:** [http://localhost:8000](http://localhost:8000)

### 2. Check health and UI

- Open [http://localhost:8000/api/health](http://localhost:8000/api/health) — expected: `{"status":"healthy"}`
- Open [http://localhost:3000](http://localhost:3000) — you should see "Image Analysis Agent" and the Navbar (Tag Image, Search, theme toggle).

### 3. Environment variables

- Backend and frontend use the root `.env` via `env_file: .env` in docker-compose.
- Frontend `NEXT_PUBLIC_API_URL` is set at build time (default `http://localhost:8000` in docker-compose). To change it, rebuild with `--build-arg NEXT_PUBLIC_API_URL=<url>`.

See [docs/quickstart/DOCKER_SETUP.md](../quickstart/DOCKER_SETUP.md) for logs, volumes, and pushing to a registry.

## How to Test

1. `GET http://localhost:8000/api/health` returns `{"status":"healthy"}`.
2. [http://localhost:3000](http://localhost:3000) shows the Navbar, "Image Analysis Agent" on `/`, and "Search" on `/search`. Theme toggle switches light/dark.

## Local run (without Docker)

If you need to run without Docker:

- **Backend:** `cd backend && pip install -r requirements.txt && uvicorn src.server:app --reload --host 0.0.0.0 --port 8000`
- **Frontend:** `cd frontend && npm install && npm run dev` (and set `NEXT_PUBLIC_API_URL=http://localhost:8000` in `.env.local`)

## Troubleshooting


| Issue                                        | Fix                                                                                                                                                        |
| -------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `OPENAI_API_KEY` error when starting backend | Ensure project root `.env` has `OPENAI_API_KEY=...`. For Phase 0 you can temporarily avoid importing settings in server.py (server doesn’t import it yet). |
| CORS errors from frontend                    | Backend already allows all origins. Ensure you’re calling `http://localhost:8000` and that the backend is running.                                         |
| Frontend build errors                        | Run `npm install` in `frontend/` and ensure Node 18+.                                                                                                      |
| Port 8000 or 3000 in use                     | Change port: `uvicorn ... --port 8001` or `npm run dev -- -p 3001`.                                                                                        |
| Docker: frontend cannot reach API            | Ensure `NEXT_PUBLIC_API_URL` is the URL the **browser** uses (e.g. `http://localhost:8000`). Rebuild frontend after changing it.                           |


