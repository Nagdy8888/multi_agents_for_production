# 08 — Node: Preprocessor

This document describes the **image_preprocessor** node: where it lives, what it does step-by-step, constants, error returns, and that it is synchronous (not async).

---

## File and function

**File:** `backend/src/image_tagging/nodes/preprocessor.py`

**Signature:** `def image_preprocessor(state: ImageTaggingState) -> dict[str, Any]`

**Type:** Synchronous (no `async`). LangGraph supports both sync and async nodes.

---

## Constants

| Name | Value | Purpose |
|------|-------|---------|
| ALLOWED_EXTENSIONS | {".jpg", ".jpeg", ".png", ".webp"} | Used for validation elsewhere (e.g. server); preprocessor itself does not check extension, only that it can decode and open as image. |
| MAX_LONG_EDGE | 1024 | Maximum length of the longer side of the image in pixels; if exceeded, image is resized proportionally. |

---

## Step-by-step behavior

1. **Read image_base64 from state.** If missing, return `{"processing_status": "failed", "error": "Missing image_base64 in state"}`.
2. **Base64-decode** the string. On exception return `{"processing_status": "failed", "error": "Invalid base64: {e}"}`.
3. **Open with PIL:** `Image.open(io.BytesIO(raw)).convert("RGB")`. On exception (unsupported format, corrupt data) return `{"processing_status": "failed", "error": "Unsupported image format: {e}"}`.
4. **Dimensions:** Read `width`, `height`; set `format_name = img.format or "JPEG"`.
5. **Resize if needed:** Compute `long_edge = max(width, height)`. If `long_edge > MAX_LONG_EDGE` (1024), compute ratio `MAX_LONG_EDGE / long_edge`, new dimensions `new_w`, `new_h`, resize with `Image.Resampling.LANCZOS`, then update `width`, `height` to the new size.
6. **Re-encode:** Write image to a `BytesIO` buffer as JPEG with quality 88, rewind, base64-encode the buffer contents to UTF-8 string.
7. **Build metadata:** `metadata = {"width": width, "height": height, "format": format_name}`.
8. **Return:** `{"image_base64": new_base64, "metadata": metadata}`.

---

## Success return shape

```python
{
    "image_base64": str,  # New base64 string (possibly resized, always JPEG)
    "metadata": {"width": int, "height": int, "format": str}
}
```

---

## Error returns

All error returns set `processing_status` to `"failed"` and include an `error` message string. Downstream nodes (e.g. vision_analyzer) may check `processing_status` or `error`; the graph continues but the final result will reflect the failure.

- Missing `image_base64`: `{"processing_status": "failed", "error": "Missing image_base64 in state"}`.
- Invalid base64: `{"processing_status": "failed", "error": "Invalid base64: ..."}`.
- Unsupported/corrupt image: `{"processing_status": "failed", "error": "Unsupported image format: ..."}`.

---

## Downstream

- **vision_analyzer** reads `state["image_base64"]` (the updated one from preprocessor) and `state["metadata"]` is available for logging or future use. The preprocessor does not set `processing_status` on success; later nodes or the aggregator set it when the pipeline completes or fails.

See [03-langgraph-pipeline.md](03-langgraph-pipeline.md) for where this node sits in the graph and [04-agent-state.md](04-agent-state.md) for state fields.
