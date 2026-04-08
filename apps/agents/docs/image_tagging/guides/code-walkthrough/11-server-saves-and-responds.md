# Lab 11 — Server Saves and Responds

**Estimated time:** 25 min  
**Difficulty:** Beginner

After **graph.ainvoke(initial_state)** returns, the server has the full **result** (final state). It optionally saves the tag record to the database, builds **tags_by_category** for the response, and returns a JSON object to the frontend. This lab traces that post-graph code in server.py.

---

## Learning objectives

- See how the server checks **SUPABASE_ENABLED** and calls **upsert_tag_record** (and how DB failures are handled without failing the request).
- See how **tags_by_category** is built from validated_tags (or from partial_tags if validated is empty).
- See the exact shape of the JSON response returned to the frontend.

---

## Prerequisites

- [10-aggregator-builds-record.md](10-aggregator-builds-record.md) — the graph has returned result with tag_record, processing_status, validated_tags, flagged_tags, etc.

---

## Step 1 — Persist to DB when Supabase is enabled

The server tries to save the tag record to the database only if Supabase is configured. If the save fails, it logs a warning but does not change the HTTP response or status code.

**Snippet (lines 111–131 in server.py)**

```python
    # Persist to DB when Supabase is enabled
    saved_to_db = False
    try:
        from src.services.supabase import SUPABASE_ENABLED, get_client
        if SUPABASE_ENABLED:
            client = get_client()
            if client:
                tag_record = result.get("tag_record")
                if isinstance(tag_record, dict):
                    client.upsert_tag_record(
                        image_id=result.get("image_id", image_id),
                        tag_record=tag_record,
                        image_url=image_url,
                        needs_review=bool(result.get("flagged_tags")),
                        processing_status=result.get("processing_status", "complete"),
                    )
                    saved_to_db = True
    except Exception as e:
        # Log but do not fail the request
        import logging
        logging.getLogger(__name__).warning("Failed to save tag record to DB: %s", e)
```

**What is happening**

- **SUPABASE_ENABLED** — From env/settings. If False we skip DB entirely.
- **get_client()** — Returns a Supabase client (or None if connection fails). If None we do not call upsert.
- **upsert_tag_record** — Inserts or updates a row in the image_tags table. The client builds **search_index** from tag_record (see Lab 18) and runs INSERT ... ON CONFLICT DO UPDATE. We pass image_id, tag_record, image_url, needs_review (True if there are any flagged tags), and processing_status.
- **saved_to_db** — Set to True only when upsert actually runs. The frontend uses this to show "Analysis saved to database" (Lab 01).
- **except** — Any exception (e.g. connection error, constraint error) is logged. We do **not** re-raise; the request still returns 200 and the full result. The user gets their analysis; only persistence failed.

**Source:** [backend/src/server.py](../../backend/src/server.py) (lines 111–131)

> **Why This Way?** The analysis result is the main outcome. DB save is secondary; if it fails, we still want to return the result so the user can see it. The client can retry or the admin can fix the DB later.

---

## Step 2 — Build tags_by_category

The frontend expects a **tags_by_category** dict: category → list of {value, confidence}. We build it from **validated_tags** (after confidence filter). If validated_tags is empty (e.g. validator returned {}), we fall back to **partial_tags** so the UI still has something to show.

**Snippet (lines 133–149 in server.py)**

```python
    # tags_by_category: dict category -> list of {value, confidence} (from validated or partial)
    validated = result.get("validated_tags") or {}
    partial = result.get("partial_tags") or []
    tags_by_category = {}
    for cat, tag_list in validated.items():
        tags_by_category[cat] = [
            {"value": t.get("value"), "confidence": t.get("confidence", 0)}
            for t in tag_list if isinstance(t, dict)
        ]
    if not tags_by_category and partial:
        for item in partial:
            if isinstance(item, dict) and item.get("category"):
                cat = item["category"]
                scores = item.get("confidence_scores") or {}
                tags_by_category[cat] = [
                    {"value": v, "confidence": scores.get(v, 0)} for v in (item.get("tags") or [])
                ]
```

**What is happening**

- **From validated_tags** — Each entry is a list of dicts with "value" and "confidence". We map each to {"value": ..., "confidence": ...} for the response.
- **Fallback to partial_tags** — If validated_tags is empty (e.g. REQUIRED_CATEGORIES gate in validator), we build tags_by_category from partial_tags: each item has category, tags (list of values), and confidence_scores (value → number). We output the same shape so the frontend does not need to handle two formats.

**Source:** [backend/src/server.py](../../backend/src/server.py) (lines 133–149)

---

## Step 3 — Return the full response

The server returns a single JSON object with every field the frontend needs to display the result and to know whether it was saved.

**Snippet (lines 150–161 in server.py)**

```python
    return {
        "image_url": result.get("image_url", image_url),
        "image_id": result.get("image_id", image_id),
        "vision_description": result.get("vision_description", ""),
        "vision_raw_tags": result.get("vision_raw_tags", {}),
        "partial_tags": result.get("partial_tags", []),
        "tags_by_category": tags_by_category,
        "tag_record": result.get("tag_record"),
        "flagged_tags": result.get("flagged_tags", []),
        "processing_status": result.get("processing_status", "complete"),
        "saved_to_db": saved_to_db,
    }
```

**What is happening**

- **image_url, image_id** — From result (or fallback to the ones we built in Lab 02). Used for the image preview and for linking to the stored record.
- **vision_description, vision_raw_tags** — From the vision node. The UI can show the description and raw JSON (e.g. dominant_mood, visible_subjects).
- **partial_tags** — The 8 TagResults from the taggers (before validation). Useful for debugging or fallback display.
- **tags_by_category** — The dict we just built. The main data the DashboardResult uses to render tags per category (Lab 12).
- **tag_record** — The final TagRecord from the aggregator. Used for search index and for detail views.
- **flagged_tags** — List of FlaggedTag dicts. The UI can show "needs review" and list low-confidence or invalid tags.
- **processing_status** — "complete", "needs_review", or "failed". The UI can show a badge or message.
- **saved_to_db** — Boolean so the frontend can show a toast like "Analysis saved to database" (Lab 01).

> **I/O Snapshot:** **Input:** result (final state from graph), image_id, image_url from Lab 02. **Output:** JSON response with the keys above. The frontend receives this in the fetch response and passes it to setAnalysisResult (Lab 01), then DashboardResult renders it (Lab 12).

> **Next:** Execution returns to the frontend. The fetch in handleAnalyze receives this JSON; setAnalysisResult(data) is called; the next render shows DashboardResult. See [12-frontend-shows-result.md](12-frontend-shows-result.md).

---

## Lab summary

1. **DB persist:** If SUPABASE_ENABLED and get_client() succeed, we call **upsert_tag_record** with image_id, tag_record, image_url, needs_review, processing_status. On any exception we log and leave saved_to_db False; we do not fail the request.
2. **tags_by_category:** Built from validated_tags (value + confidence per tag). If validated is empty we build from partial_tags so the UI still has per-category tags.
3. **Response:** We return a dict with image_url, image_id, vision_description, vision_raw_tags, partial_tags, tags_by_category, tag_record, flagged_tags, processing_status, saved_to_db. This becomes the body of the HTTP 200 response to the frontend.

---

## Exercises

1. Why does the server not raise an exception when upsert_tag_record fails?
2. When would tags_by_category be built from partial_tags instead of validated_tags?
3. What does the frontend do with saved_to_db? (Hint: Lab 01.)

---

## Next lab

Go to [12-frontend-shows-result.md](12-frontend-shows-result.md) to see how the Home page renders DashboardResult with the analysis data and how each sub-component (TagCategories, FlaggedTags, ConfidenceRing, etc.) uses the response.
