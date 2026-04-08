# Docker setup

Run the full stack with Docker Compose.

## Quick start

From the project root:

```bash
docker compose up --build
```

- **App:** http://localhost:3000  
- **API:** http://localhost:8000  

## Environment

Create a `.env` file at the project root (same directory as `docker-compose.yml`):

```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o
# Optional: Supabase/PostgreSQL for save and search
DATABASE_URI=postgresql://user:password@host:5432/postgres
```

The backend and frontend services both use this `.env` via `env_file`. The frontend build is given `NEXT_PUBLIC_API_URL=http://localhost:8000` so the browser can call the API on your machine.

## Services

| Service   | Port | Description                    |
|----------|------|--------------------------------|
| backend  | 8000 | FastAPI + LangGraph, uploads  |
| frontend | 3000 | Next.js app                   |

Uploads are stored in a Docker volume `backend_uploads` so they persist across restarts.

## Logs and troubleshooting

- **View logs:** `docker compose logs -f`
- **Rebuild after code changes:** `docker compose up --build`
- **Backend fails on startup:** Check `.env` has `OPENAI_API_KEY`. Backend loads `.env` from the project root (mounted or copied at build time; for env vars, `env_file` passes them at run).
- **Frontend build fails:** Fix any TypeScript/ESLint errors reported in the build output.
- **Database (503):** If you see 503 on tag-images or search, the app is running without a DB. Set `DATABASE_URI` and run `backend/src/services/supabase/migration.sql` in your Supabase SQL editor, then restart: `docker compose up --build`.

## Pushing images to a registry

To build and push for a registry:

```bash
docker compose build
docker tag image-analysis-agent-backend:latest your-registry/image-analysis-agent-backend:latest
docker tag image-analysis-agent-frontend:latest your-registry/image-analysis-agent-frontend:latest
docker push your-registry/image-analysis-agent-backend:latest
docker push your-registry/image-analysis-agent-frontend:latest
```

In production, set `NEXT_PUBLIC_API_URL` to the public URL of your backend (e.g. `https://api.yourdomain.com`) when building the frontend image.
