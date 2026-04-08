# Lab 17 — Bulk Polling and Completion

**Estimated time:** 20 min  
**Difficulty:** Beginner

The frontend **BulkUploader** submits files to POST /api/bulk-upload, receives **batch_id**, then **polls** GET /api/bulk-status/{batch_id} at an interval (e.g. 2 s) until **status** is "complete". It updates **batchState** so the UI can show progress (completed/total) and per-file results (image_url or error). This lab traces the polling loop and completion handling.

---

## Learning objectives

- See how **useEffect** starts a polling interval when batchId is set and status is not "complete".
- See how **bulk_status** returns BATCH_STORAGE[batch_id] (total, completed, results, status).
- See how the frontend clears the interval when status becomes "complete" and updates the UI.

---

## Prerequisites

- [16-bulk-upload-and-background.md](16-bulk-upload-and-background.md) — the server has returned batch_id and is processing in the background.

---

## Step 1 — BulkUploader: polling with useEffect

After POST bulk-upload the component has **batchId** and initial **batchState**. A **useEffect** runs when batchId or batchState.status changes: if we have a batchId and status is not "complete", it calls **fetch(bulk-status/{batchId})**, then **setBatchState(data)**. If the backend uses an interval (or the frontend does), the effect can set **setInterval** to call the same fetch every 2 s; when **data.status === "complete"** we **clearInterval** and stop polling.

**Source:** [frontend/src/components/BulkUploader.tsx](../../frontend/src/components/BulkUploader.tsx) — look for useEffect with batchId, fetch to bulk-status, setBatchState, and interval cleanup when complete.

---

## Step 2 — bulk_status endpoint

**Snippet (server.py)**

```python
@app.get("/api/bulk-status/{batch_id}")
def bulk_status(batch_id: str):
    if batch_id not in BATCH_STORAGE:
        raise HTTPException(status_code=404, detail="Batch not found")
    return BATCH_STORAGE[batch_id]
```

The response is the dict: **total**, **completed**, **results** (list of {image_id, status, image_url? | error?}), **status** ("processing" | "complete"). The frontend uses this to render progress and the list of results.

**Source:** [backend/src/server.py](../../backend/src/server.py) (lines 377–382)

---

## Lab summary

- BulkUploader polls GET bulk-status/{batch_id} until status is "complete", then stops. bulk_status returns BATCH_STORAGE[batch_id]. The UI shows completed/total and per-file outcome.

---

## Next lab

[18-database-deep-dive.md](18-database-deep-dive.md) — migration schema and SupabaseClient methods.
