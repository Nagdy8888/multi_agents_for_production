# API reference

FastAPI app: `backend/src/server.py`. Base URL in Docker: http://localhost:8000.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/health | Health check; returns `{"status":"healthy"}` |
| GET | /api/taxonomy | Full tag taxonomy (all categories and values) |
| POST | /api/analyze-image | Upload one image; run pipeline; return tags + tag_record. Body: multipart `file`. Returns 503 if graph/DB error (after retries). |
| GET | /api/tag-image/{image_id} | One stored row by image_id. 404 if not found, 503 if DB disabled. |
| GET | /api/tag-images | List recent tag records. Query: `limit`, `offset`. 503 if DB disabled. |
| GET | /api/search-images | Filtered search. Query: `season`, `theme`, `objects`, `dominant_colors`, `design_elements`, `occasion`, `mood`, `product_type` (comma-separated), `limit`. 503 if DB disabled. |
| GET | /api/available-filters | Cascading filter values for current selection. Same query params as search-images. 503 if DB disabled. |
| POST | /api/bulk-upload | Multiple images. Body: multipart `files`. Returns `{ batch_id, total, status }`. |
| GET | /api/bulk-status/{batch_id} | Batch progress: `{ total, completed, results[], status }`. 404 if batch unknown. |

Static uploads: `GET /uploads/{filename}` serves files from backend uploads directory.

## Example: analyze one image

```bash
curl -X POST http://localhost:8000/api/analyze-image -F "file=@image.jpg"
```

Response (trimmed): `image_url`, `image_id`, `vision_description`, `vision_raw_tags`, `tags_by_category`, `tag_record`, `flagged_tags`, `processing_status`, `saved_to_db`.

## Example: search

```bash
curl "http://localhost:8000/api/search-images?season=christmas&theme=modern&limit=20"
```

Returns `{ "items": [ ... ], "limit": 20 }` where each item has `image_id`, `tag_record`, `image_url`, `processing_status`, etc.
