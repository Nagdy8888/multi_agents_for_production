# Lab 16 — Bulk Upload and Background Task

**Estimated time:** 25 min  
**Difficulty:** Intermediate

**Bulk upload** accepts multiple files in one request, creates a **batch_id**, stores the batch in **BATCH_STORAGE**, and starts a **background task** that processes each file (save, run graph, upsert to DB). The endpoint returns immediately with batch_id and status "processing". This lab traces bulk_upload, BATCH_STORAGE, _run_bulk_batch, and _process_one_file.

---

## Learning objectives

- See how **bulk_upload** reads all files into memory, creates BATCH_STORAGE[batch_id], and starts **asyncio.create_task(run())** so the response returns immediately.
- See **_process_one_file**: same pipeline as single analyze (save file, initial_state, graph.ainvoke, upsert) but updates **BATCH_STORAGE[batch_id]["results"][index]** and increments **completed**; when completed >= total, status becomes "complete".
- Understand that BATCH_STORAGE is in-memory and keyed by batch_id.

---

## Prerequisites

- [11-server-saves-and-responds.md](11-server-saves-and-responds.md) — _process_one_file reuses the same graph and DB logic.

---

## Step 1 — bulk_upload: read files, create batch, start background task

**Snippet (lines 357–376 in server.py)**

```python
@app.post("/api/bulk-upload")
async def bulk_upload(request: Request, files: list[UploadFile] = File(..., alias="files")):
    if not files:
        raise HTTPException(status_code=400, detail="At least one file required")
    file_list: list[tuple[str, bytes]] = []
    for f in files:
        contents = await f.read()
        file_list.append((f.filename or "image.jpg", contents))
    batch_id = str(uuid.uuid4())
    total = len(file_list)
    BATCH_STORAGE[batch_id] = {
        "total": total,
        "completed": 0,
        "results": [{"image_id": "", "status": "pending"} for _ in range(total)],
        "status": "processing",
    }
    _run_bulk_batch(request, batch_id, file_list)
    return {"batch_id": batch_id, "total": total, "status": "processing"}
```

**What is happening**

- We read every file into memory as (filename, contents). **batch_id** is a new UUID. **BATCH_STORAGE[batch_id]** holds total, completed (0), results (one slot per file, status "pending"), and status "processing". **_run_bulk_batch** starts the async loop in a **background task** via asyncio.create_task. The handler then returns immediately so the client gets batch_id and can poll bulk-status.

**Source:** [backend/src/server.py](../../backend/src/server.py) (lines 357–376)

---

## Step 2 — _run_bulk_batch and _process_one_file

**_run_bulk_batch** defines an async function **run()** that loops over file_list and awaits **_process_one_file** for each. It starts it with **asyncio.create_task(run())** so the event loop runs it in the background.

**_process_one_file** does: validate extension → save file → build initial_state → **graph.ainvoke(initial_state)** → upsert to DB if enabled → write to **BATCH_STORAGE[batch_id]["results"][index]** (image_id, status "complete" or "failed", image_url or error) → increment **completed** → if completed >= total set status to "complete".

**Source:** [backend/src/server.py](../../backend/src/server.py) (lines 347–355, 286–345)

> **Next:** [17-bulk-polling-and-completion.md](17-bulk-polling-and-completion.md) — frontend polling and completion UI.

---

## Lab summary

- **bulk_upload** stores files and batch state in BATCH_STORAGE and starts a background task. **_process_one_file** runs the full pipeline per file and updates results and completed; when all are done, status becomes "complete".

---

## Next lab

[17-bulk-polling-and-completion.md](17-bulk-polling-and-completion.md)
