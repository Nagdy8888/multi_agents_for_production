# Feature checklist

| Feature | Status | Notes |
|---------|--------|--------|
| Single image upload (UI) | Done | Drag-and-drop, analyze button |
| POST /api/analyze-image | Done | Multipart file, LangGraph pipeline |
| Vision analysis (GPT-4o) | Done | Description + raw tags |
| 8 category taggers | Done | Season, theme, objects, colors, design, occasion, mood, product |
| Validator + confidence filter | Done | Taxonomy check, thresholds |
| Tag record aggregation | Done | tag_record, processing_status |
| Save to DB (Supabase) | Done | When DATABASE_URI set |
| GET tag-image, tag-images | Done | 503 if DB disabled |
| Search by filters | Done | GET search-images, available-filters |
| Search page UI | Done | FilterSidebar, SearchResults, DetailModal |
| Bulk upload (API) | Done | POST bulk-upload, GET bulk-status |
| Bulk upload (UI) | Done | BulkUploader, progress, per-file status |
| History grid | Done | Recently tagged images, Refresh |
| Saved badge + toast | Done | When saved_to_db |
| Error handling | Done | Global handler, retry in vision/taggers, DB retry |
| Empty states + skeletons | Done | HistoryGrid, SearchResults, error page |
| Focus / a11y | Done | focus-visible styles |
| Docker + compose | Done | backend + frontend services |
| Documentation | Done | Quickstart, architecture, reports, curriculum |
| CHANGELOG + README | Done | Phases and quick start |
