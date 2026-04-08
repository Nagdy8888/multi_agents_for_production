# 17 — API Reference

This document lists every HTTP endpoint: method, path, query/body parameters, request/response shapes with examples, status codes, and error handling. It also summarizes the single-analyze lifecycle, bulk (BATCH_STORAGE, _process_one_file, _run_bulk_batch, polling), search (_parse_filter_params), and the global exception handler.

---

## Base URL and global error handling

- **Base URL:** When running via Docker Compose, frontend uses `NEXT_PUBLIC_API_URL` (e.g. http://localhost:8000). Backend serves on port 8000.
- **Global exception handler:** Any unhandled exception in the FastAPI app returns **500** with body `{"detail": "<str(exc)>", "type": "<exception type name>"}`. The server also logs the full traceback.

---

## Endpoints

### GET /api/health

- **Purpose:** Liveness check.
- **Response:** `200` — `{"status": "healthy"}`.

---

### GET /api/taxonomy

- **Purpose:** Return full tag taxonomy (categories and allowed values).
- **Response:** `200` — JSON object: keys are category names (season, theme, objects, dominant_colors, design_elements, occasion, mood, product_type); values are either lists (flat) or dicts (hierarchical). Same shape as `TAXONOMY` in backend.

**Example:**

```json
{
  "season": ["christmas", "hanukkah", "..."],
  "theme": ["whimsical", "traditional", "..."],
  "objects": { "characters": ["santa", "..."], "animals": ["bear", "..."], "..." },
  "dominant_colors": { "red_family": ["crimson", "..."], "..." },
  "design_elements": ["stripes", "..."],
  "occasion": ["gifting_general", "..."],
  "mood": ["joyful_fun", "..."],
  "product_type": { "gift_bag": ["gift_bag_small", "..."], "..." }
}
```

---

### POST /api/analyze-image

- **Purpose:** Upload one image, run the LangGraph pipeline, optionally save to DB, return analysis.
- **Request:** `multipart/form-data` with one file field: **file** (image: JPG, PNG, WEBP). Allowed extensions: .jpg, .jpeg, .png, .webp.
- **Response:** `200` — JSON with image_url, image_id, vision_description, vision_raw_tags, partial_tags, tags_by_category, tag_record, flagged_tags, processing_status, saved_to_db.
- **Errors:** `400` — Invalid file type (detail: "Invalid file type. Allowed: JPG, PNG, WEBP."). `500` — Graph load or analysis failure (detail string).

**Response example:**

```json
{
  "image_url": "http://localhost:8000/uploads/a1b2c3d4-....jpg",
  "image_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "vision_description": "A red gift box with gold ribbon...",
  "vision_raw_tags": { "visual_description": "...", "dominant_mood": "festive", "..." },
  "partial_tags": [{ "category": "season", "tags": ["christmas"], "confidence_scores": { "christmas": 0.92 } }, "..." ],
  "tags_by_category": {
    "season": [{ "value": "christmas", "confidence": 0.92 }],
    "theme": [{ "value": "traditional", "confidence": 0.88 }],
    "..."
  },
  "tag_record": { "image_id": "...", "season": ["christmas"], "..." },
  "flagged_tags": [],
  "processing_status": "complete",
  "saved_to_db": true
}
```

**Single-analyze lifecycle:** Request file → validate type → save to uploads/ → base64 encode → build initial_state → graph.ainvoke(initial_state) → if DB enabled, upsert_tag_record → build tags_by_category from validated_tags (or partial_tags fallback) → return JSON.

---

### GET /api/tag-image/{image_id}

- **Purpose:** Fetch one stored tag record by image_id.
- **Path:** image_id (UUID string).
- **Response:** `200` — One row: image_id, tag_record, search_index, image_url, needs_review, processing_status, created_at, updated_at.
- **Errors:** `503` — Database not configured or not available (detail string). `404` — Image not found.

---

### GET /api/tag-images

- **Purpose:** List recently tagged images (for history).
- **Query:** limit (int, default 20), offset (int, default 0).
- **Response:** `200` — `{"items": [ {...row...}, ...], "limit": 20, "offset": 0}`. Each item has image_id, tag_record, search_index, image_url, needs_review, processing_status, created_at, updated_at.
- **Errors:** `503` — Database not configured or not available.

---

### GET /api/search-images

- **Purpose:** Search images by tag filters (AND across categories). Filters are parsed by _parse_filter_params from query params.
- **Query:** season, theme, objects, dominant_colors, design_elements, occasion, mood, product_type (each optional, comma-separated list of values); limit (int, default 50).
- **Response:** `200` — `{"items": [ {...row...}, ...], "limit": 50}`. Rows same shape as tag-images.
- **Errors:** `503` — Database not configured or not available.

**_parse_filter_params:** Takes optional query params (season=..., theme=..., etc.). For each param, splits by comma, strips, and builds a dict category → list of non-empty strings. Used by both search-images and available-filters.

---

### GET /api/available-filters

- **Purpose:** Return available filter values per category for the current selection (cascading). Backend runs search_images_filtered with current filters (limit 500), then scans tag_record of each row to collect unique values per category.
- **Query:** Same as search-images (season, theme, objects, ...).
- **Response:** `200` — `{"season": ["christmas", "..."], "theme": [...], "..."}`. Only values that appear in the current result set.
- **Errors:** `503` — Database not configured or not available.

---

### POST /api/bulk-upload

- **Purpose:** Upload multiple images; start background processing; return batch_id for polling.
- **Request:** `multipart/form-data` with **files** (array of image files). Server reads all file contents into memory immediately, then spawns background task.
- **Response:** `200` — `{"batch_id": "<uuid>", "total": N, "status": "processing"}`.
- **Errors:** `400` — No files (detail: "At least one file required").

**Bulk flow:** BATCH_STORAGE[batch_id] = { total, completed: 0, results: [{ image_id: "", status: "pending" }, ...], status: "processing" }. _run_bulk_batch(request, batch_id, file_list) runs asyncio.create_task(run()) where run() calls _process_one_file for each (filename, contents). _process_one_file: validate extension, save file, graph.ainvoke, optional upsert_tag_record, set results[index] and increment completed; when completed >= total set status to "complete". Frontend polls GET /api/bulk-status/{batch_id} until status is "complete" or all results are filled.

---

### GET /api/bulk-status/{batch_id}

- **Purpose:** Return current batch state for polling.
- **Path:** batch_id (UUID string).
- **Response:** `200` — Same object as stored in BATCH_STORAGE: `{ "total": N, "completed": M, "results": [ { "image_id": "...", "status": "pending"|"processing"|"complete"|"failed", "image_url"?: "...", "error"?: "..." }, ... ], "status": "processing"|"complete" }`.
- **Errors:** `404` — Batch not found.

---

## Static files

- **GET /uploads/{filename}** — Served by FastAPI StaticFiles from backend/uploads/. Used for image_url in responses.

---

## CORS

- CORSMiddleware allows origins=["*"], credentials=True, methods=["*"], headers=["*"].
