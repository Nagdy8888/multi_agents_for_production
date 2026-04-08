# Lab 04 — Preprocessor Runs

**Estimated time:** 25 min  
**Difficulty:** Beginner

The first node that runs when the graph executes is the **preprocessor**. It reads `image_base64` from state, decodes it, opens it as an image, resizes if the long edge exceeds 1024 px, re-encodes as JPEG, and returns updated state. This lab walks through the code line by line.

---

## Learning objectives

- See how a graph node receives state and returns a dict of updates.
- Understand decode → open (PIL) → resize → encode → base64.
- Understand error handling: missing data or invalid image returns failed state.

---

## Prerequisites

- [03-graph-starts.md](03-graph-starts.md) — the graph has been compiled and `ainvoke` has started; the first node is the preprocessor.

---

## Step 1 — Node signature and read image_base64

The preprocessor is a **sync** function (not async). It receives the current state and returns a dict; LangGraph merges that dict into the state.

**Snippet (lines 15–22 in preprocessor.py)**

```python
def image_preprocessor(state: ImageTaggingState) -> dict[str, Any]:
    """Validate image, resize to max 1024px on long edge, set metadata and base64."""
    image_base64 = state.get("image_base64")
    if not image_base64:
        return {
            "processing_status": "failed",
            "error": "Missing image_base64 in state",
        }
```

**What is happening**

- **state** — The current graph state. At this point it has `image_id`, `image_url`, `image_base64`, and `partial_tags` (from the server’s initial_state). Other keys are not set yet.
- **state.get("image_base64")** — Safe way to get a key that might be missing. Returns `None` if absent.
- If there is no `image_base64`, we return immediately with `processing_status: "failed"` and an error message. The graph will still continue to the next nodes (vision, taggers, etc.), but later nodes and the aggregator will see the failed status and can short-circuit or surface the error.

**Source:** [backend/src/image_tagging/nodes/preprocessor.py](../../backend/src/image_tagging/nodes/preprocessor.py) (lines 15–22)

> **State Tracker (input):** `image_id`, `image_url`, `image_base64` (long string), `partial_tags: []`. Rest empty.

> **Error Path:** If `image_base64` is missing, we return failed state. The vision node and taggers may still run with empty description; the aggregator sets `processing_status` from state (including "failed"). The API response will include the error.

---

## Step 2 — Decode base64 and open with PIL

We decode the base64 string to raw bytes and open it as an image using the PIL (Pillow) library.

**Snippet (lines 24–33 in preprocessor.py)**

```python
    try:
        raw = base64.b64decode(image_base64)
    except Exception as e:
        return {"processing_status": "failed", "error": f"Invalid base64: {e}"}

    try:
        img = Image.open(io.BytesIO(raw)).convert("RGB")
    except Exception as e:
        return {"processing_status": "failed", "error": f"Unsupported image format: {e}"}
```

**What is happening**

- **base64.b64decode(image_base64)** — Converts the base64 string back to bytes. If the string is malformed, it raises; we catch and return a failed state with a message.
- **io.BytesIO(raw)** — Wraps the bytes in a file-like object so PIL can read from it.
- **Image.open(...)** — PIL detects the format (JPEG, PNG, etc.) and decodes the image. If the data is not a valid image, it raises; we catch and return "Unsupported image format".
- **.convert("RGB")** — Converts to RGB so we have a single format for resizing and re-encoding. Some images have transparency (PNG); RGB is 3 channels and saves as JPEG without issues.

> **Glossary:** **PIL / Pillow** — Python Imaging Library; used to open, resize, and save images in memory.

---

## Step 3 — Dimensions and optional resize

We read width and height; if the long edge is greater than 1024 px, we resize proportionally.

**Snippet (lines 33–43 in preprocessor.py)**

```python
    width, height = img.size
    format_name = img.format or "JPEG"

    # Resize if long edge > MAX_LONG_EDGE
    long_edge = max(width, height)
    if long_edge > MAX_LONG_EDGE:
        ratio = MAX_LONG_EDGE / long_edge
        new_w = int(width * ratio)
        new_h = int(height * ratio)
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        width, height = new_w, new_h
```

**What is happening**

- **img.size** — Tuple (width, height) in pixels.
- **format_name** — Original format (JPEG, PNG, etc.); we use it only for metadata. After resize we always output JPEG.
- **MAX_LONG_EDGE = 1024** (defined at top of file). We resize only when the longer side exceeds 1024 to limit token/cost and latency for the vision API.
- **ratio** — Scale factor so that the long edge becomes 1024. We apply the same ratio to both dimensions to keep aspect ratio.
- **img.resize(..., Image.Resampling.LANCZOS)** — High-quality resampling. We update `img` and then `width, height` for the metadata we return.

> **Why This Way?** Large images mean more tokens and slower API calls. Capping at 1024 keeps quality good enough for tagging while controlling cost and speed.

---

## Step 4 — Re-encode to JPEG and base64

We write the (possibly resized) image to a buffer as JPEG, then base64-encode that buffer.

**Snippet (lines 45–58 in preprocessor.py)**

```python
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=88)
    buf.seek(0)
    new_base64 = base64.b64encode(buf.read()).decode("utf-8")

    metadata = {
        "width": width,
        "height": height,
        "format": format_name,
    }

    return {
        "image_base64": new_base64,
        "metadata": metadata,
    }
```

**What is happening**

- **io.BytesIO()** — In-memory buffer to write the image bytes.
- **img.save(buf, format="JPEG", quality=88)** — Encodes the image as JPEG with quality 88 and writes to the buffer.
- **buf.seek(0)** — Moves the read position back to the start so we can read the buffer.
- **buf.read()** — Reads all bytes from the buffer. **base64.b64encode(...).decode("utf-8")** produces the string we put back into state.
- **metadata** — We return width, height, and original format for logging or debugging. Downstream nodes do not have to use it.
- **return** — We return only the keys we change: `image_base64` (replaced with the new, possibly resized image) and `metadata`. LangGraph merges this into the state; the next node (vision_analyzer) will see the updated `image_base64`.

> **State Tracker (after preprocessor):** Same as before except: `image_base64` is the new string (possibly smaller), `metadata` is set. `vision_description`, `vision_raw_tags`, `partial_tags`, etc. still not set.

> **I/O Snapshot:** **Input (state):** `image_base64` = long string (e.g. 200 KB of base64). **Output (return):** `image_base64` = new string (smaller if resized), `metadata` = `{ "width": 800, "height": 600, "format": "JPEG" }`.

> **Next:** Execution continues at the **vision_analyzer** node. See [05-vision-calls-gpt4o.md](05-vision-calls-gpt4o.md).

---

## Lab summary

1. Preprocessor reads `image_base64` from state; if missing or invalid (decode/open fails), it returns failed state.
2. Image is opened with PIL, converted to RGB, and optionally resized so the long edge is at most 1024 px.
3. Image is re-encoded as JPEG (quality 88) and base64; that string and metadata are returned. LangGraph merges them into state; the vision node then uses the new `image_base64`.

---

## Exercises

1. Why convert to RGB before saving as JPEG?
2. If the image is already 800×600, does the preprocessor still produce new base64? Why?
3. What does the vision node receive in state if the preprocessor returned failed?

---

## Next lab

Go to [05-vision-calls-gpt4o.md](05-vision-calls-gpt4o.md) to see how the vision analyzer builds a multimodal message, calls GPT-4o, retries on failure, and parses the JSON response into `vision_description` and `vision_raw_tags`.
