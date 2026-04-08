# Lab 02 — Server Receives Image

**Estimated time:** 25 min  
**Difficulty:** Beginner

The FastAPI server receives the POST request at `/api/analyze-image`, validates the file type, saves the file to disk, builds the initial state for the graph, and invokes the pipeline. This lab traces that code with exact line numbers.

---

## Learning objectives

- See how FastAPI receives an uploaded file and validates extension and content type.
- See how the server generates an image ID, saves bytes to disk, and builds a base64 string for the graph.
- Understand the shape of `initial_state` passed into the graph.

---

## Prerequisites

- [01-user-clicks-analyze.md](01-user-clicks-analyze.md) — the frontend has sent `POST /api/analyze-image` with FormData.

---

## Step 1 — Route and file parameter

FastAPI matches the request to the route and injects the uploaded file into the function parameter.

> **File Type — .py:** Python source file. The backend is written in Python.

**Snippet (lines 66–67 in server.py)**

```python
@app.post("/api/analyze-image")
async def analyze_image(request: Request, file: UploadFile = File(..., alias="file")):
```

**What is happening**

- `@app.post("/api/analyze-image")` registers this function for `POST` requests to `/api/analyze-image`. The `app` is the FastAPI application.
- `async def` means the function is asynchronous; we can use `await` inside it.
- `request: Request` gives access to the full request (e.g. `request.base_url` for building the image URL later).
- `file: UploadFile = File(..., alias="file")` tells FastAPI to read the form field named `"file"` (the one the frontend sent with `formData.append("file", file)`) and pass it as an `UploadFile` object. The `...` means the parameter is required.

**Source:** [backend/src/server.py](../../backend/src/server.py) (lines 66–67)

> **Glossary:** **endpoint** — One URL + HTTP method (e.g. POST /api/analyze-image) that the server handles.

> **Error Path:** If the client sends no `file` field, FastAPI returns 422 Unprocessable Entity before this function runs. If the client sends a different content type, we validate it in the next step.

---

## Step 2 — Validate file type

The server only allows certain image types. If the file does not match, it returns 400 and the function stops.

**Snippet (lines 68–78 in server.py)**

```python
    # Validate file type
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Allowed: JPG, PNG, WEBP.",
        )
    if file.content_type and file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Allowed: JPG, PNG, WEBP.",
        )
```

**What is happening**

- `file.filename` is the original name (e.g. `"photo.jpg"`). `Path(...).suffix` gets the extension (e.g. `.jpg`). We use `.lower()` so `.JPG` is allowed.
- `ALLOWED_IMAGE_EXTENSIONS` is `{".jpg", ".jpeg", ".png", ".webp"}` (defined at top of server.py). If the extension is not in that set, we raise `HTTPException` with status 400. FastAPI turns that into an HTTP 400 response with a JSON body `{"detail": "Invalid file type. Allowed: JPG, PNG, WEBP."}`.
- We also check `file.content_type` (e.g. `"image/jpeg"`) against `ALLOWED_CONTENT_TYPES` so we do not accept a file renamed to `.jpg` but with a non-image content type.

> **State Tracker:** No state yet; we are only validating. If we pass, we proceed to save.

> **Error Path:** If validation fails, `HTTPException` is raised and the function exits. The client receives 400 and the message in `detail`. The frontend catch block in Lab 01 will set `error` to that message.

---

## Step 3 — Save file and build paths

The server generates a unique ID, saves the file bytes to disk, and builds the URL that the frontend will use to display the image.

**Snippet (lines 80–88 in server.py)**

```python
    # Save file
    image_id = str(uuid.uuid4())
    filename = f"{image_id}{suffix}"
    filepath = UPLOADS_DIR / filename
    contents = await file.read()
    filepath.write_bytes(contents)

    base_url = str(request.base_url).rstrip("/")
    image_url = f"{base_url}/uploads/{filename}"
```

**What is happening**

- `uuid.uuid4()` generates a unique ID; we convert it to string (e.g. `"a1b2c3d4-..."`). That becomes the image identifier for the whole pipeline and the database.
- `filename` is that ID plus the original extension (e.g. `a1b2c3d4-....jpg`) so the file on disk has a unique name and we keep the extension.
- `UPLOADS_DIR` is the backend’s `uploads` directory (see top of server.py). `filepath = UPLOADS_DIR / filename` is the full path to the file.
- `await file.read()` reads the entire uploaded file into memory as bytes. The graph and vision API will need the image data; we also write it to disk so we can serve it later at `/uploads/{filename}`.
- `filepath.write_bytes(contents)` writes those bytes to disk. The file is now available as a static file (FastAPI mounts `UPLOADS_DIR` at `/uploads`).
- `request.base_url` is the server’s base URL (e.g. `http://localhost:8000/`). We strip a trailing slash and then form `image_url = "http://localhost:8000/uploads/a1b2c3d4-....jpg"`. The frontend and API responses use this URL to show the image.

**Source:** [backend/src/server.py](../../backend/src/server.py) (lines 80–88)

> **Why This Way?** We save to disk so the image can be served over HTTP and so we have a stable path. The graph gets the same bytes as base64 so it does not need to read from disk again.

---

## Step 4 — Base64 for the graph

The LangGraph pipeline expects the image as base64 in state (so the preprocessor and vision node can use it). We encode the same bytes we saved.

**Snippet (lines 89–91 in server.py)**

```python
    # Base64 for graph (preprocessor expects raw then resizes)
    image_base64 = base64.b64encode(contents).decode("utf-8")
```

**What is happening**

- `base64.b64encode(contents)` turns the raw bytes into base64 bytes.
- `.decode("utf-8")` turns those bytes into a string. The state and the vision API expect a string (e.g. `"iVBORw0KGgo..."`), not raw bytes.

> **I/O Snapshot:** **Input:** `contents` (bytes, e.g. 50 KB of JPEG). **Output:** `image_base64` (string, longer, safe to put in JSON and in API payloads).

---

## Step 5 — Import graph and build initial state

The graph is built in another module. We import it here and build the dict that LangGraph will pass through the pipeline.

**Snippet (lines 93–103 in server.py)**

```python
    try:
        from src.image_tagging.image_tagging import graph
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graph load error: {e}")

    initial_state = {
        "image_id": image_id,
        "image_url": image_url,
        "image_base64": image_base64,
        "partial_tags": [],
    }
```

**What is happening**

- The graph is created when `image_tagging` is first imported (it calls `build_graph()` and compiles). We import it here so that graph construction and any import errors happen when the first request runs, not at server startup.
- If the import fails (e.g. missing dependency), we raise HTTP 500 with a message so the client knows the server misconfigured.
- `initial_state` is a plain dict. It must match the shape expected by the graph: `image_id`, `image_url`, `image_base64`, and `partial_tags` (empty list). The reducer for `partial_tags` will merge tagger outputs into this list. Other state keys (vision_description, validated_tags, tag_record, etc.) are added by nodes later.

> **State Tracker (initial_state):** Only these keys are set: `image_id`, `image_url`, `image_base64`, `partial_tags: []`. All other fields the pipeline will use are absent; nodes add them as they run.

> **I/O Snapshot:** **initial_state** (excerpt): `{ "image_id": "a1b2c3d4-...", "image_url": "http://localhost:8000/uploads/a1b2c3d4-....jpg", "image_base64": "iVBORw0KGgo...", "partial_tags": [] }`.

---

## Step 6 — Invoke the graph

The server runs the full pipeline by calling `graph.ainvoke(initial_state)`. Execution moves into the graph until every node has run.

**Snippet (lines 105–108 in server.py)**

```python
    try:
        result = await graph.ainvoke(initial_state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")
```

**What is happening**

- `graph.ainvoke(initial_state)` runs the compiled graph: it passes `initial_state` into the first node (preprocessor), then follows edges through vision, taggers, validator, confidence filter, and aggregator. The return value is the final state after all nodes have run.
- `await` waits for the whole pipeline to finish. This may take many seconds (vision + 8 taggers + validation + aggregation).
- If any node raises an exception (e.g. API error, parse error), we catch it and return 500 with a generic "Analysis failed" message (we could log the full exception server-side).

> **Next:** Execution continues **inside the graph**. The first node that runs is the preprocessor (Lab 04). How the graph is built (nodes and edges) is explained in [03-graph-starts.md](03-graph-starts.md). The preprocessor code is in [04-preprocessor-runs.md](04-preprocessor-runs.md).

---

## Lab summary

1. FastAPI receives the file via the `file` parameter (form field `"file"`).
2. We validate extension and content type; if invalid, we return 400.
3. We generate `image_id`, save the file to `uploads/`, build `image_url`, and encode the image as `image_base64`.
4. We import the graph and build `initial_state` with those four keys plus `partial_tags: []`.
5. We call `graph.ainvoke(initial_state)`; the pipeline runs (Labs 04–10). When it returns, `result` holds the full state (including `tag_record`, `processing_status`, etc.). The server then uses that to save to the DB and build the response (Lab 11).

---

## Exercises

1. Why do we validate both `suffix` and `content_type`?
2. What would happen if we did not call `await file.read()` and instead passed `file` directly into the graph?
3. Where is the graph object actually created (in which file and at which line)? (Hint: Lab 03.)

---

## Next lab

Go to [03-graph-starts.md](03-graph-starts.md) to see how the graph is built (StateGraph, nodes, edges, compile). Then [04-preprocessor-runs.md](04-preprocessor-runs.md) to see the first node that runs when `ainvoke` is called.
