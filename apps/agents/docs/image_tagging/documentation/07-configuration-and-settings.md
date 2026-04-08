# 07 — Configuration and Settings

This document describes how configuration is loaded (env from project root `.env`) and lists every setting: `settings.py` (OpenAI, optional LangChain and DB) and `configuration.py` (thresholds, overrides, MAX_*). It also explains how overrides interact with the confidence filter and how to tune thresholds.

---

## Where configuration lives

- **Agent/env:** `backend/src/image_tagging/settings.py` — loads project root `.env`, defines OPENAI and LangChain vars.
- **Supabase/DB:** `backend/src/services/supabase/settings.py` — loads project root `.env`, defines DATABASE_URI and SUPABASE_ENABLED.
- **Agent constants:** `backend/src/image_tagging/configuration.py` — thresholds, overrides, MAX_COLORS, MAX_OBJECTS.

---

## settings.py (image_tagging)

**File:** `backend/src/image_tagging/settings.py`

- **Load:** `load_dotenv(_project_root / ".env")` where `_project_root` is the directory above `backend/` (repository root). So the **project root** `.env` is used.
- **OPENAI_API_KEY:** `os.getenv("OPENAI_API_KEY")`. If missing, the module raises `ValueError("OPENAI_API_KEY is required. Set it in the project root .env file.")`.
- **OPENAI_MODEL:** `os.getenv("OPENAI_MODEL", "gpt-4o")`. Default is `"gpt-4o"`.
- **DATABASE_URI:** Not in image_tagging settings; see Supabase settings below.
- **LANGCHAIN_API_KEY:** `os.getenv("LANGCHAIN_API_KEY")` — optional; for LangSmith tracing.
- **LANGCHAIN_TRACING_V2:** `os.getenv("LANGCHAIN_TRACING_V2", "false").lower() in ("true", "1", "yes")` — optional; enables tracing when true.

---

## settings.py (Supabase)

**File:** `backend/src/services/supabase/settings.py`

- **Load:** Same pattern: `load_dotenv(_project_root / ".env")`.
- **DATABASE_URI:** `os.getenv("DATABASE_URI", "").strip()`. PostgreSQL connection string (e.g. Supabase connection URI).
- **SUPABASE_ENABLED:** `bool(DATABASE_URI)`. If `DATABASE_URI` is set and non-empty, persistence and search are enabled; otherwise DB routes return 503 or skip writes.

---

## configuration.py

**File:** `backend/src/image_tagging/configuration.py`

| Constant | Value | Purpose |
|----------|-------|---------|
| CONFIDENCE_THRESHOLD | 0.65 | Default minimum confidence for a tag to stay in validated_tags; below this it is moved to flagged_tags with reason "low_confidence". |
| NEEDS_REVIEW_THRESHOLD | 3 | If, in a single category, at least this many tags are moved to flagged (low_confidence), needs_review is set true. |
| MAX_COLORS | 5 | Cap on number of dominant_colors tags per image (tag_colors tagger). |
| MAX_OBJECTS | 10 | Cap on number of objects tags per image (tag_objects tagger). |
| VISION_MODEL | OPENAI_MODEL | Model used for vision (from settings). |
| TAGGER_MODEL | OPENAI_MODEL | Model used for taggers (from settings). |
| CATEGORY_CONFIDENCE_OVERRIDES | {"product_type": 0.80, "season": 0.60} | Per-category confidence thresholds. product_type must be ≥ 0.80 to pass; season can pass at ≥ 0.60. Other categories use CONFIDENCE_THRESHOLD (0.65). |

---

## How overrides interact with the confidence filter

- **Confidence filter** ([13-node-confidence-filter.md](13-node-confidence-filter.md)) reads `validated_tags` and, for each category, gets a threshold:
  - If the category is in `CATEGORY_CONFIDENCE_OVERRIDES`, use that value (e.g. product_type 0.80, season 0.60).
  - Otherwise use `CONFIDENCE_THRESHOLD` (0.65).
- Tags with confidence **≥** that threshold stay in `validated_tags`; tags **below** are appended to `flagged_tags` with reason `"low_confidence"`.
- So:
  - **season** at 0.62 passes (0.62 ≥ 0.60).
  - **product_type** at 0.78 is flagged (0.78 < 0.80).
  - **theme** at 0.64 is flagged (0.64 < 0.65).

---

## Tuning thresholds

- **Stricter tagging (fewer false positives):** Increase `CONFIDENCE_THRESHOLD` (e.g. 0.75) or add/raise overrides in `CATEGORY_CONFIDENCE_OVERRIDES` (e.g. theme: 0.75).
- **Looser tagging (more tags, more review):** Decrease `CONFIDENCE_THRESHOLD` (e.g. 0.55) or lower overrides (e.g. season: 0.55).
- **More “needs review”:** Decrease `NEEDS_REVIEW_THRESHOLD` (e.g. 2) so fewer low-confidence tags per category trigger review.
- **Fewer colors/objects per image:** Decrease `MAX_COLORS` or `MAX_OBJECTS` in configuration.py (taggers already use these caps).

All of these are read at import time from `configuration.py` and `settings.py`; changing `.env` or the Python constants and restarting the server applies the new values.
