"""Unified FastAPI entry-point for the Multi-Agent Platform.

Combines PO parser webhook and image tagging REST API into one app.
"""
from __future__ import annotations

import asyncio
import base64
import logging
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv
from fastapi import BackgroundTasks, Depends, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from src.api.middleware import verify_webhook_secret
from src.po_parser.schemas.email import IncomingEmail

load_dotenv()

_level = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO)
logging.basicConfig(level=_level)
logger = logging.getLogger(__name__)

# uploads/ lives at apps/agents/uploads/
UPLOADS_DIR = Path(__file__).resolve().parent.parent.parent / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}

BATCH_STORAGE: dict[str, dict] = {}


def _public_base_url(request: Request) -> str:
    """Origin used in persisted /uploads URLs so browsers can load images (Search, history).

    Behind ngrok/Docker, ``request.base_url`` is often ``http://127.0.0.1:8000``. Order:
    ``API_PUBLIC_BASE_URL``, ``X-Forwarded-*``, ``NEXT_PUBLIC_API_URL`` (same URL the UI uses
    for API calls), then ``request.base_url``.
    """
    explicit = (os.getenv("API_PUBLIC_BASE_URL") or "").strip().rstrip("/")
    if explicit:
        return explicit
    xf_proto = request.headers.get("x-forwarded-proto")
    xf_host = request.headers.get("x-forwarded-host")
    if xf_proto and xf_host:
        proto = xf_proto.split(",")[0].strip()
        host = xf_host.split(",")[0].strip()
        if proto and host:
            return f"{proto}://{host}"
    next_api = (os.getenv("NEXT_PUBLIC_API_URL") or "").strip().rstrip("/")
    if next_api:
        return next_api
    return str(request.base_url).rstrip("/")


def _canonical_origin_for_rewrite() -> str | None:
    """Prefer API_PUBLIC_BASE_URL, else NEXT_PUBLIC_API_URL (for fixing stored rows)."""
    for key in ("API_PUBLIC_BASE_URL", "NEXT_PUBLIC_API_URL"):
        v = (os.getenv(key) or "").strip().rstrip("/")
        if v:
            return v
    return None


def _rewrite_uploads_url(url: str | None) -> str | None:
    """Rewrite /uploads/* so it always uses the canonical origin the browser can reach.

    Stored URLs may point at 127.0.0.1, a Docker service name, or a stale ngrok subdomain
    that no longer matches the running tunnel. We normalise all of them.
    """
    if not url or "/uploads/" not in url:
        return url
    canon = _canonical_origin_for_rewrite()
    if not canon:
        return url
    expected_prefix = canon.rstrip("/") + "/uploads/"
    if url.startswith(expected_prefix):
        return url
    rest = url.split("/uploads/", 1)[1]
    return f"{canon}/uploads/{rest}"


def _rewrite_tag_row(row: dict) -> dict:
    out = dict(row)
    iu = out.get("image_url")
    if iu:
        out["image_url"] = _rewrite_uploads_url(iu)
    return out


app = FastAPI(title="Multi-Agent Platform")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "type": type(exc).__name__},
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")


# ---------------------------------------------------------------------------
# PO Parser endpoints
# ---------------------------------------------------------------------------

def _run_pipeline(email: IncomingEmail) -> None:
    from src.po_parser.po_parser import graph

    initial = {
        "email": email,
        "classification": None,
        "extracted_po": None,
        "normalized_po": None,
        "validation": None,
        "airtable_record_id": None,
        "airtable_url": None,
        "gas_callback_status": None,
        "errors": [],
        "processing_start_time": time.time(),
    }
    try:
        graph.invoke(initial)
    except Exception:
        logger.exception("Pipeline failed for message_id=%s", email.message_id)


@app.get("/health")
def health() -> dict:
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/webhook/email")
def webhook_email(
    email: IncomingEmail,
    background_tasks: BackgroundTasks,
    _: None = Depends(verify_webhook_secret),
) -> JSONResponse:
    background_tasks.add_task(_run_pipeline, email)
    return JSONResponse(
        status_code=202,
        content={"status": "accepted", "message_id": email.message_id},
    )


# ---------------------------------------------------------------------------
# Image Tagging endpoints
# ---------------------------------------------------------------------------

@app.get("/api/taxonomy")
def get_taxonomy():
    from src.image_tagging.taxonomy import TAXONOMY
    return TAXONOMY


@app.post("/api/analyze-image")
async def analyze_image(request: Request, file: UploadFile = File(..., alias="file")):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Invalid file type. Allowed: JPG, PNG, WEBP.")
    if file.content_type and file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Invalid file type. Allowed: JPG, PNG, WEBP.")

    image_id = str(uuid.uuid4())
    filename = f"{image_id}{suffix}"
    filepath = UPLOADS_DIR / filename
    contents = await file.read()
    filepath.write_bytes(contents)

    base_url = _public_base_url(request)
    image_url = f"{base_url}/uploads/{filename}"
    image_base64 = base64.b64encode(contents).decode("utf-8")

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

    try:
        result = await graph.ainvoke(initial_state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")

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
        logger.warning("Failed to save tag record to DB: %s", e)

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

    out_url = result.get("image_url", image_url)
    return {
        "image_url": _rewrite_uploads_url(out_url) if out_url else out_url,
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


@app.get("/api/tag-image/{image_id}")
def get_tag_image(image_id: str):
    try:
        from src.services.supabase import SUPABASE_ENABLED, get_client
    except ImportError:
        raise HTTPException(status_code=503, detail="Database not available")
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Database not configured")
    client = get_client()
    if not client:
        raise HTTPException(status_code=503, detail="Database not available")
    row = client.get_tag_record(image_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Image not found")
    return _rewrite_tag_row(row)


@app.get("/api/tag-images")
def list_tag_images(limit: int = 20, offset: int = 0):
    try:
        from src.services.supabase import SUPABASE_ENABLED, get_client
    except ImportError:
        raise HTTPException(status_code=503, detail="Database not available")
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Database not configured")
    client = get_client()
    if not client:
        raise HTTPException(status_code=503, detail="Database not available")
    rows = client.list_tag_images(limit=limit, offset=offset)
    return {"items": [_rewrite_tag_row(r) for r in rows], "limit": limit, "offset": offset}


def _parse_filter_params(
    season: str | None = None,
    theme: str | None = None,
    objects: str | None = None,
    dominant_colors: str | None = None,
    design_elements: str | None = None,
    occasion: str | None = None,
    mood: str | None = None,
    product_type: str | None = None,
) -> dict[str, list[str]]:
    filters = {}
    for key, param in [
        ("season", season), ("theme", theme), ("objects", objects),
        ("dominant_colors", dominant_colors), ("design_elements", design_elements),
        ("occasion", occasion), ("mood", mood), ("product_type", product_type),
    ]:
        if param:
            values = [v.strip() for v in param.split(",") if v.strip()]
            if values:
                filters[key] = values
    return filters


@app.get("/api/search-images")
def search_images(
    season: str | None = None,
    theme: str | None = None,
    objects: str | None = None,
    dominant_colors: str | None = None,
    design_elements: str | None = None,
    occasion: str | None = None,
    mood: str | None = None,
    product_type: str | None = None,
    limit: int = 50,
):
    try:
        from src.services.supabase import SUPABASE_ENABLED, get_client
    except ImportError:
        raise HTTPException(status_code=503, detail="Database not available")
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Database not configured")
    client = get_client()
    if not client:
        raise HTTPException(status_code=503, detail="Database not available")
    filters = _parse_filter_params(
        season=season, theme=theme, objects=objects, dominant_colors=dominant_colors,
        design_elements=design_elements, occasion=occasion, mood=mood, product_type=product_type,
    )
    rows = client.search_images_filtered(filters, limit=limit)
    return {"items": [_rewrite_tag_row(r) for r in rows], "limit": limit}


@app.get("/api/available-filters")
def available_filters(
    season: str | None = None,
    theme: str | None = None,
    objects: str | None = None,
    dominant_colors: str | None = None,
    design_elements: str | None = None,
    occasion: str | None = None,
    mood: str | None = None,
    product_type: str | None = None,
):
    try:
        from src.services.supabase import SUPABASE_ENABLED, get_client
    except ImportError:
        raise HTTPException(status_code=503, detail="Database not available")
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Database not configured")
    client = get_client()
    if not client:
        raise HTTPException(status_code=503, detail="Database not available")
    filters = _parse_filter_params(
        season=season, theme=theme, objects=objects, dominant_colors=dominant_colors,
        design_elements=design_elements, occasion=occasion, mood=mood, product_type=product_type,
    )
    return client.get_available_filter_values(filters)


async def _process_one_file(
    request: Request,
    filename_orig: str,
    contents: bytes,
    batch_id: str,
    index: int,
) -> None:
    image_id = ""
    try:
        suffix = Path(filename_orig or "").suffix.lower()
        if suffix not in ALLOWED_IMAGE_EXTENSIONS:
            BATCH_STORAGE[batch_id]["results"][index] = {"image_id": "", "status": "failed", "error": "Invalid file type"}
            BATCH_STORAGE[batch_id]["completed"] += 1
            return
        image_id = str(uuid.uuid4())
        filename = f"{image_id}{suffix}"
        filepath = UPLOADS_DIR / filename
        filepath.write_bytes(contents)
        base_url = _public_base_url(request)
        image_url = f"{base_url}/uploads/{filename}"
        image_base64 = base64.b64encode(contents).decode("utf-8")
        from src.image_tagging.image_tagging import graph
        initial_state = {
            "image_id": image_id,
            "image_url": image_url,
            "image_base64": image_base64,
            "partial_tags": [],
        }
        result = await graph.ainvoke(initial_state)
        tag_record = result.get("tag_record")
        try:
            from src.services.supabase import SUPABASE_ENABLED, get_client
            if SUPABASE_ENABLED and isinstance(tag_record, dict):
                client = get_client()
                if client:
                    client.upsert_tag_record(
                        image_id=image_id,
                        tag_record=tag_record,
                        image_url=image_url,
                        needs_review=bool(result.get("flagged_tags")),
                        processing_status=result.get("processing_status", "complete"),
                    )
        except Exception as e:
            logger.warning("Bulk save to DB failed for %s: %s", image_id, e)
        BATCH_STORAGE[batch_id]["results"][index] = {
            "image_id": image_id,
            "status": "complete",
            "image_url": image_url,
        }
    except Exception as e:
        logger.exception("Bulk process failed for file %s: %s", index, e)
        BATCH_STORAGE[batch_id]["results"][index] = {
            "image_id": image_id or "",
            "status": "failed",
            "error": str(e),
        }
    BATCH_STORAGE[batch_id]["completed"] += 1
    if BATCH_STORAGE[batch_id]["completed"] >= BATCH_STORAGE[batch_id]["total"]:
        BATCH_STORAGE[batch_id]["status"] = "complete"


def _run_bulk_batch(request: Request, batch_id: str, file_list: list[tuple[str, bytes]]):
    async def run():
        for i, (filename_orig, contents) in enumerate(file_list):
            await _process_one_file(request, filename_orig, contents, batch_id, i)
    asyncio.create_task(run())


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


@app.get("/api/bulk-status/{batch_id}")
def bulk_status(batch_id: str):
    if batch_id not in BATCH_STORAGE:
        raise HTTPException(status_code=404, detail="Batch not found")
    payload = BATCH_STORAGE[batch_id]
    out = dict(payload)
    if isinstance(out.get("results"), list):
        out["results"] = [
            _rewrite_tag_row(dict(r)) if isinstance(r, dict) else r for r in out["results"]
        ]
    return out


# ---------------------------------------------------------------------------
# GAS Drive Image webhook (new endpoint for image tagger GAS integration)
# ---------------------------------------------------------------------------

@app.post("/webhook/drive-image")
async def webhook_drive_image(request: Request, background_tasks: BackgroundTasks):
    """Accept a base64 image from GAS DriveTrigger, process it, and call back GAS with results."""
    body = await request.json()

    secret = body.get("secret") or request.headers.get("x-webhook-secret", "")
    expected = os.getenv("WEBHOOK_SECRET", "")
    if not secret or secret != expected:
        raise HTTPException(status_code=403, detail="Invalid webhook secret")

    image_b64 = body.get("image_base64", "")
    filename_orig = body.get("filename", "image.jpg")
    drive_file_id = body.get("drive_file_id", "")

    if not image_b64:
        raise HTTPException(status_code=400, detail="image_base64 is required")

    contents = base64.b64decode(image_b64)
    suffix = Path(filename_orig).suffix.lower()
    if suffix not in ALLOWED_IMAGE_EXTENSIONS:
        suffix = ".jpg"

    image_id = str(uuid.uuid4())
    filename = f"{image_id}{suffix}"
    filepath = UPLOADS_DIR / filename
    filepath.write_bytes(contents)

    base_url = _public_base_url(request)
    image_url = f"{base_url}/uploads/{filename}"

    async def _process():
        start = time.time()
        try:
            from src.image_tagging.image_tagging import graph
            initial_state = {
                "image_id": image_id,
                "image_url": image_url,
                "image_base64": base64.b64encode(contents).decode("utf-8"),
                "partial_tags": [],
            }
            result = await graph.ainvoke(initial_state)

            try:
                from src.services.supabase import SUPABASE_ENABLED, get_client
                if SUPABASE_ENABLED:
                    client = get_client()
                    if client:
                        tag_record = result.get("tag_record")
                        if isinstance(tag_record, dict):
                            client.upsert_tag_record(
                                image_id=image_id,
                                tag_record=tag_record,
                                image_url=image_url,
                                needs_review=bool(result.get("flagged_tags")),
                                processing_status=result.get("processing_status", "complete"),
                            )
            except Exception as e:
                logger.warning("Drive-image DB save failed: %s", e)

            try:
                from src.services.gas_callback import GASCallbackClient
                gas_client = GASCallbackClient()
                await gas_client.send_results_async({
                    "type": "image_result",
                    "status": "success",
                    "image_id": image_id,
                    "filename": filename_orig,
                    "drive_file_id": drive_file_id,
                    "tag_record": result.get("tag_record"),
                    "confidence": result.get("tag_record", {}).get("confidence"),
                    "processing_status": result.get("processing_status", "complete"),
                    "processing_time_ms": int((time.time() - start) * 1000),
                })
            except Exception as e:
                logger.warning("GAS callback failed for drive-image %s: %s", image_id, e)

        except Exception as e:
            logger.exception("Drive-image processing failed for %s: %s", image_id, e)
            try:
                from src.services.gas_callback import GASCallbackClient
                gas_client = GASCallbackClient()
                await gas_client.send_results_async({
                    "type": "image_result",
                    "status": "error",
                    "image_id": image_id,
                    "filename": filename_orig,
                    "drive_file_id": drive_file_id,
                    "errors": [str(e)],
                    "processing_time_ms": int((time.time() - start) * 1000),
                })
            except Exception:
                logger.exception("GAS error callback also failed for %s", image_id)

    background_tasks.add_task(_process)

    return JSONResponse(
        status_code=202,
        content={"status": "accepted", "image_id": image_id, "drive_file_id": drive_file_id},
    )