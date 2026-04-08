# Local setup (without Docker)

Run the backend and frontend on your machine for development.

## Prerequisites

- Python 3.11+
- Node.js 20+
- (Optional) Supabase/PostgreSQL for persistence and search

## 1. Clone and backend

```bash
cd image-analysis-agent
cd backend
pip install -r requirements.txt
```

Create a `.env` file at the **project root** (parent of `backend/`):

```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o
# Optional: for save and search
DATABASE_URI=postgresql://user:password@host:5432/postgres
```

Run the API:

```bash
cd backend
uvicorn src.server:app --reload --host 0.0.0.0 --port 8000
```

API: http://localhost:8000 — try `GET /api/health`.

## 2. Frontend

```bash
cd frontend
npm install
```

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Run the app:

```bash
npm run dev
```

App: http://localhost:3000

## 3. Database (optional)

To enable save and search, run the migration in Supabase SQL editor: `backend/src/services/supabase/migration.sql`. Set `DATABASE_URI` in the root `.env` as above.

## Troubleshooting

- **Backend "OPENAI_API_KEY not set"** — ensure `.env` is at project root and contains `OPENAI_API_KEY`.
- **Frontend can't reach API** — ensure `NEXT_PUBLIC_API_URL` matches where the backend is running (e.g. `http://localhost:8000`).
- **503 on /api/tag-images or /api/search-images** — database is disabled; set `DATABASE_URI` and run the migration.
