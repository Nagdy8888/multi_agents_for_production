"""Image preprocessor: validate format, resize to max 1024, extract metadata (spec 4.1)."""
import base64
import io
from typing import Any

from PIL import Image

from ..schemas.states import ImageTaggingState

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_LONG_EDGE = 1024


def image_preprocessor(state: ImageTaggingState) -> dict[str, Any]:
    """Validate image, resize to max 1024px on long edge, set metadata and base64."""
    image_base64 = state.get("image_base64")
    if not image_base64:
        return {
            "processing_status": "failed",
            "error": "Missing image_base64 in state",
        }

    try:
        raw = base64.b64decode(image_base64)
    except Exception as e:
        return {"processing_status": "failed", "error": f"Invalid base64: {e}"}

    try:
        img = Image.open(io.BytesIO(raw)).convert("RGB")
    except Exception as e:
        return {"processing_status": "failed", "error": f"Unsupported image format: {e}"}

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
