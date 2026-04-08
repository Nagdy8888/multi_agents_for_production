# Image Tagging Agent — Detailed Project Summary

## 1. Purpose and Function of the Project

### What It Does

The **Image Tagging Agent** is an AI-powered system that:

1. **Analyzes product images** (e.g. gift bags, gift cards, wrapping paper) and assigns **structured, predefined tags** across eight categories.
2. **Stores** the results in a database (Supabase/PostgreSQL) so images can be **searched and filtered** by those tags.
3. Supports **single-image upload**, **bulk upload**, and a **search UI** so users can find images by season, theme, colors, occasion, mood, and more.

### Why It Exists

- **Problem:** Large image libraries are hard to organize and search without consistent, manual tagging.
- **Solution:** A single vision model pass plus eight parallel “tagger” steps produce a **TagRecord** (all categories, confidence scores, and flags for human review). Tags are **enum-only** (from a fixed taxonomy), so search and filters stay consistent.
- **Outcome:** Upload images → get tags automatically → save to DB → search/filter in the UI or via API. Batch and single-image workflows are both supported.

### Key Constraints (from spec)

- All tag values are **predefined** (no free-form text).
- Some categories are **hierarchical** (e.g. parent/child for objects, colors, product type); both levels are stored and searchable.
- Each tag has a **confidence score** (0.0–1.0); low-confidence tags are **flagged for human review**.
- The system is built for **single-image and batch** use.

---

## 2. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND (Next.js)                               │
│  Dashboard (upload, results, save, history) │ Search (filters, detail modal)   │
│  Bulk uploader (multi-file, progress)       │ Navbar, theme toggle            │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                          HTTP (NEXT_PUBLIC_API_URL, default :8000)
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           BACKEND (FastAPI)                                  │
│  src/server.py — routes: analyze-image, tag-image, tag-images, taxonomy,     │
│                  search-images, available-filters, bulk-upload, bulk-status  │
│  Serves /uploads for stored image files                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AGENT (LangGraph, src/image_tagging/)                     │
│  preprocessor → vision (GPT-4o) → [8 parallel taggers] → validator →         │
│  confidence_filter → tag_aggregator → TagRecord                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                          optional (SUPABASE_ENABLED)
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     DATABASE (Supabase / PostgreSQL)                         │
│  image_tags: image_id, tag_record (JSONB), search_index (TEXT[]),            │
│              image_url, needs_review, processing_status, created_at, updated_at│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Backend (Detailed)

### 3.1 Technology Stack

- **Runtime:** Python 3.11+
- **Framework:** FastAPI
- **Agent orchestration:** LangGraph
- **Vision / LLM:** OpenAI GPT-4o (via LangChain / langchain-openai)
- **Database client:** psycopg2 (PostgreSQL); connection via **DATABASE_URL** (Supabase or any Postgres).
- **Other:** Pillow (image handling), python-dotenv, httpx, pydantic.

### 3.2 Where the Code Lives

| Path | Role |
|------|------|
| **src/server.py** | FastAPI app: CORS, static `/uploads`, all API routes, calls graph and Supabase client. |
| **src/image_tagging/** | LangGraph agent: state, taxonomy, graph definition, and all nodes. |
| **src/image_tagging/graph_builder.py** | Builds the graph: edges, conditional fan-out to taggers, fan-in to validator. |
| **src/image_tagging/image_tagging.py** | Exposes the compiled `graph` (used by server). |
| **src/image_tagging/taxonomy.py** | Single source of truth for allowed tag values (SEASON, THEME, OBJECTS, etc.). |
| **src/image_tagging/schemas/** | State (e.g. ImageTaggingState) and tag models (TagResult, TagRecord, FlaggedTag, etc.). |
| **src/image_tagging/nodes/** | One or more nodes per file: preprocessor, vision, taggers, validator, confidence, aggregator. |
| **src/image_tagging/prompts/** | Prompt templates for vision and taggers. |
| **src/services/supabase/** | DB client: build_search_index, upsert_tag_record, get_tag_record, list_tag_images, search_images_filtered, get_available_filter_values. |

### 3.3 Pipeline (LangGraph) Step by Step

1. **image_preprocessor** — Validates image format, can resize, builds base64 and metadata for the vision step.
2. **vision_analyzer** — One GPT-4o vision call; returns a structured description and raw tags (vision_description, vision_raw_tags).
3. **Eight taggers (parallel via Send API):**  
   season_tagger, theme_tagger, objects_tagger, color_tagger (dominant_colors), design_tagger, occasion_tagger, mood_tagger, product_tagger.  
   Each reads the vision output and taxonomy, returns **partial_tags** (category, tags, confidence_scores).
4. **tag_validator** — Ensures every tag value exists in the taxonomy; invalid tags go into **flagged_tags**.
5. **confidence_filter** — Applies a confidence threshold; low-confidence tags are flagged; if many are flagged in one category, sets **needs_review**.
6. **tag_aggregator** — Assembles **TagRecord** (all eight categories, needs_review, processed_at, etc.) and sets **processing_status**.

State is passed through the graph; reducers (e.g. for partial_tags) merge results from parallel taggers.

### 3.4 API Endpoints (Summary)

| Method | Path | Function |
|--------|------|----------|
| GET | /api/health | Health check. |
| POST | /api/analyze-image | Upload one image; run graph; return vision, tags_by_category, tag_record, flagged_tags, saved_to_db. Optionally writes to DB if SUPABASE_ENABLED. |
| GET | /api/tag-image/{image_id} | Fetch one stored record by image_id. |
| GET | /api/tag-images | List recent tagged images (history); query: limit, offset. |
| GET | /api/taxonomy | Return full taxonomy for UI dropdowns (flat and hierarchical). |
| GET | /api/search-images | Filter by category query params (season, theme, objects, etc.); returns matching items. |
| GET | /api/available-filters | Same query params as search; returns only filter values that exist in the current result set (cascading filters). |
| POST | /api/bulk-upload | Multiple files; creates a batch job; returns batch_id. |
| GET | /api/bulk-status/{batch_id} | Progress and results for a bulk job. |

Uploaded files are stored under **uploads/** and served at **/uploads/{filename}**; the backend mounts this directory as static files.

### 3.5 Database (Supabase / PostgreSQL)

- **Table:** `image_tags`  
  - **image_id** (PK), **tag_record** (JSONB), **search_index** (TEXT[]), **needs_review**, **processing_status**, **image_url**, **created_at**, **updated_at**.
- **Indexes:** GIN on search_index (and optionally on tag_record) for fast filtered search.
- **Client** (in src/services/supabase/client.py):  
  build_search_index, upsert_tag_record, get_tag_record, list_tag_images, search_images_filtered, get_available_filter_values.  
- If **DATABASE_URL** is not set or **SUPABASE_ENABLED** is false, the server still runs but does not write or read from the DB (tag-image/tag-images may return 503 or empty).

---

## 4. Frontend (Detailed)

### 4.1 Technology Stack

- **Framework:** Next.js 16 (App Router)
- **UI:** React 19, TypeScript
- **Styling:** Tailwind CSS v4, PostCSS
- **Other:** Framer Motion (animations), Lucide React (icons), react-dropzone (file upload), react-syntax-highlighter (JSON display).

### 4.2 Where the Code Lives

- **app/** — App Router: `layout.tsx` (theme, fonts), `page.tsx` (dashboard), `search/page.tsx` (search page), `globals.css`.
- **components/** — Reusable UI: Navbar, ThemeProvider, ThemeToggle, ImageUploader, ProcessingOverlay, JsonViewer, ConfidenceRing, TagCategories, TagCategoryCard, TagChip, FlaggedTags, SaveToast, HistoryGrid, FilterDropdown, DetailModal, BulkUploader.
- **lib/** — types (AnalyzeImageResponse, TagRecord, TaxonomyResponse, SearchFilters, etc.), constants (e.g. API_BASE_URL), visionMapper (maps vision_raw_tags to category tags for display).

### 4.3 Main Screens and Flows

- **Dashboard (home, `/`)**  
  - Upload one image (ImageUploader / dropzone).  
  - While the backend runs the graph: ProcessingOverlay shows steps (e.g. Preprocessing → Vision → Tagging → Complete).  
  - Result: vision description, confidence ring, TagCategories (eight TagCategoryCards with TagChips), FlaggedTags (if any), raw JSON (JsonViewer).  
  - “Save” triggers the backend to persist to DB (if enabled); SaveToast shows success/failure.  
  - HistoryGrid lists recently saved images (from /api/tag-images).  
  - BulkUploader: multi-file select, “Start Bulk Analysis”, progress; on completion, history can refetch.  
  - “Analyze New Image” resets the form and preview.

- **Search (`/search`)**  
  - Sidebar: FilterDropdowns per category (accordion, chips); taxonomy comes from /api/taxonomy; selected filters call /api/search-images and /api/available-filters for cascading options.  
  - Main area: grid of result cards (image, top tags).  
  - Clicking a card opens DetailModal (full image and full tag record).  
  - Navbar links: “Tag Image” (dashboard), “Search” (search page).

### 4.4 API Usage (Frontend → Backend)

- **Dashboard:** POST /api/analyze-image (file), GET /api/tag-images (history), and save flow (handled inside analyze response or separate save call as per implementation).  
- **Search:** GET /api/taxonomy, GET /api/search-images (query params from filters), GET /api/available-filters (same params for cascading).  
- **Bulk:** POST /api/bulk-upload (files), GET /api/bulk-status/{batch_id} (polling).  
- Base URL is **NEXT_PUBLIC_API_URL** (default http://localhost:8000).

---

## 5. Data Flow (End-to-End)

1. **User** selects one or more images (dashboard or bulk).
2. **Frontend** sends file(s) to **POST /api/analyze-image** (or bulk-upload).
3. **Backend** saves the file under uploads/, builds initial state (image_id, image_url, image_base64, etc.), and runs **graph.ainvoke(initial_state)**.
4. **Graph** runs: preprocessor → vision → eight taggers (parallel) → validator → confidence_filter → aggregator → **TagRecord** (+ flagged_tags, processing_status).
5. **Backend** maps partial_tags to tags_by_category, optionally calls **Supabase** (build_search_index + upsert_tag_record) if SUPABASE_ENABLED.
6. **Backend** responds with vision_description, tags_by_category, tag_record, flagged_tags, saved_to_db, etc.
7. **Frontend** shows tags, confidence, flagged tags, and SaveToast; HistoryGrid can refetch from GET /api/tag-images.
8. On **Search** page, user picks filters → frontend calls **GET /api/search-images** and **GET /api/available-filters** → results and dropdowns update; clicking a card shows DetailModal with full TagRecord.

---

## 6. Taxonomy (Tag Categories)

Eight categories, all from **src/image_tagging/taxonomy.py** (and exposed by GET /api/taxonomy):

- **season** — e.g. christmas, easter, halloween, valentines_day, birthday, all_occasion (flat list).
- **theme** — e.g. nature, floral, vintage, modern, kids (flat list).
- **objects** — hierarchical (e.g. parent/child: characters/santa, nature/tree).
- **dominant_colors** — hierarchical (e.g. red/crimson, green/mint).
- **design_elements** — e.g. stripes, dots, foil, minimal (flat list).
- **occasion** — e.g. wedding, baby_shower, graduation, everyday (flat list).
- **mood** — e.g. playful, romantic, festive (flat list).
- **product_type** — hierarchical (e.g. gift_bags/paper, gift_cards/folded).

Flat categories are stored as arrays of strings in TagRecord; hierarchical ones as arrays of { parent, child } or a single object for product_type.

---

## 7. Deployment and Run

- **Backend:** From project root, install deps (`pip install -r requirements.txt`), set **.env** (OPENAI_API_KEY, optionally DATABASE_URL, SUPABASE_ENABLED). Run: `uvicorn src.server:app --reload --host 0.0.0.0 --port 8000`.
- **Frontend:** `npm install`, `npm run dev` (or build + start). Set **NEXT_PUBLIC_API_URL** if backend is not on localhost:8000.
- **Docker:** docker-compose builds backend and frontend images; backend serves API and uploads, frontend serves Next.js app. See **docs/quickstart/DOCKER_SETUP.md**.

---

## 8. Summary Table

| Layer | Stack | Main role |
|-------|--------|-----------|
| **Frontend** | Next.js 16, React 19, TypeScript, Tailwind, Framer Motion | Dashboard (upload, results, save, history, bulk), Search (filters, detail modal), Navbar, theme. |
| **Backend API** | FastAPI, Python 3.11+ | Routes for analyze, tag-image, tag-images, taxonomy, search-images, available-filters, bulk-upload, bulk-status; serves /uploads. |
| **Agent** | LangGraph, OpenAI GPT-4o, taxonomy | Preprocess → vision → 8 taggers → validator → confidence_filter → aggregator → TagRecord. |
| **Database** | Supabase (PostgreSQL), psycopg2 | image_tags table; search_index; filtered search and cascading filters. |

**Function of the project:** Automatically tag product images with structured, taxonomy-based labels, store them in a database, and provide a UI and API to search and filter by those tags, with support for single and bulk upload and human-review flags for low-confidence tags.
