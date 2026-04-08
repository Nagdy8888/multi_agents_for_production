# Image Tagging Dashboard

Next.js frontend for the image tagging agent. Talks to the unified API at `NEXT_PUBLIC_API_URL` (default `http://localhost:8000`).

## Dev

```bash
npm install
# Windows PowerShell:
$env:NEXT_PUBLIC_API_URL="http://localhost:8000"
npm run dev
```

Open http://localhost:3000

## Docker

Root `docker-compose` builds this image with `NEXT_PUBLIC_API_URL` from `ROOT/.env`.

## Stack

Next.js 16, React 19, TypeScript, Tailwind 4, shadcn/ui.
