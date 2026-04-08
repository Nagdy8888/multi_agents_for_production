# Project summary (executive)

**Image Analysis Agent** is a full-stack application that tags product images with structured metadata (season, theme, colors, objects, etc.) using AI. Users upload images via a web UI; the system runs a LangGraph pipeline with GPT-4o vision and optional storage in Supabase, then supports search and bulk upload.

## Features

- **Single image analysis:** Upload one image, get a description and tags in eight categories (season, theme, objects, dominant colors, design elements, occasion, mood, product type), with confidence and flagged items for review.
- **Bulk upload:** Upload multiple images; the system processes them in the background and reports progress per file.
- **Persistence and search:** When a database is configured, results are saved and users can search by tag filters (cascading filters) and view recent tagged images.
- **Docker deployment:** Backend and frontend run via Docker Compose; one command to build and run.

## Stack

- **Frontend:** Next.js, React, TypeScript, Tailwind, shadcn/ui.
- **Backend:** FastAPI, LangGraph, OpenAI GPT-4o.
- **Database:** Optional Supabase (PostgreSQL) for storage and search.

## Status

Phases 0–6 are complete: project setup, simple analyzer, LangGraph pipeline, full tagging, Supabase integration, search and bulk upload, and polish (error handling, UI, documentation). The app is ready for local or Docker-based use and can be extended with more tag categories or deployment targets.
