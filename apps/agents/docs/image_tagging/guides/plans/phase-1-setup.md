# Phase 1: Simple Image Analyzer + React UI — Setup Guide

## What This Phase Adds

- Backend `POST /api/analyze-image`: upload image, call GPT-4o vision, return description and raw tags
- Static mount `/uploads` for served images
- Frontend: ImageUploader (drag-and-drop, 10MB limit), ProcessingOverlay (3 steps), VisionResults (two-column layout), JsonViewer (collapsible raw JSON)
- Dashboard page wired with full analyze flow and error handling

## Prerequisites

- Phase 0 complete (Docker or local backend + frontend running)
- `.env` with `OPENAI_API_KEY` set

## Files Changed

| Path | Change |
|------|--------|
| `backend/src/server.py` | Mount StaticFiles, add POST /api/analyze-image (vision prompt, LangChain ChatOpenAI, JSON parse) |
| `frontend/src/lib/constants.ts` | Added (API_BASE_URL) |
| `frontend/src/lib/types.ts` | Added (AnalyzeImageResponse) |
| `frontend/src/components/ImageUploader.tsx` | Added |
| `frontend/src/components/ProcessingOverlay.tsx` | Added |
| `frontend/src/components/VisionResults.tsx` | Added |
| `frontend/src/components/JsonViewer.tsx` | Added |
| `frontend/src/app/page.tsx` | Replaced with dashboard (state, analyze flow, results) |
| `frontend/next.config.ts` | Added images.remotePatterns for localhost:8000 uploads |

## Step-by-Step Setup (Docker)

Same as Phase 0. From project root:

```bash
docker compose up --build
```

Ensure `.env` contains `OPENAI_API_KEY`. Open http://localhost:3000, upload an image, click Analyze. You should see the processing overlay, then the AI description and raw JSON.

## How to Test

1. Open http://localhost:3000
2. Drag or select a JPG/PNG/WEBP image (under 10MB)
3. Click **Analyze**
4. Overlay shows: Uploading → Analyzing with AI → Complete
5. Page shows: image preview, AI Analysis card (description, mood, subjects, colors, etc.), and “View Raw JSON” with full response
6. Click **Analyze New Image** to reset

## Troubleshooting

| Issue | Fix |
|-------|-----|
| 500 Vision analysis failed | Check `OPENAI_API_KEY` in `.env`. Ensure backend can reach OpenAI. |
| 400 Invalid file type | Use only JPG, PNG, or WEBP. |
| Image not loading in results | Backend must be reachable at `NEXT_PUBLIC_API_URL`; image_url uses backend origin. For Docker, both run on same host so localhost:8000 works. |
| CORS errors | Backend allows all origins; confirm frontend is calling the correct API URL. |
