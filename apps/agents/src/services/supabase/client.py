"""Supabase PostgreSQL client: upsert, get, list tag records."""
import json
import logging
import time

import psycopg2
from psycopg2.extras import RealDictCursor

from .settings import DATABASE_URI, SUPABASE_ENABLED

logger = logging.getLogger(__name__)


def build_search_index(tag_record: dict) -> list[str]:
    """Flatten all tag values from tag_record for search. Include parent + child for hierarchical."""
    out: set[str] = set()
    if not tag_record:
        return []

    for key in ("season", "theme", "design_elements", "occasion", "mood"):
        val = tag_record.get(key)
        if isinstance(val, list):
            for v in val:
                if isinstance(v, str):
                    out.add(v)

    for key in ("objects", "dominant_colors"):
        val = tag_record.get(key)
        if isinstance(val, list):
            for item in val:
                if isinstance(item, dict):
                    p = item.get("parent")
                    c = item.get("child")
                    if p:
                        out.add(p)
                    if c:
                        out.add(c)

    pt = tag_record.get("product_type")
    if isinstance(pt, dict):
        if pt.get("parent"):
            out.add(pt["parent"])
        if pt.get("child"):
            out.add(pt["child"])

    return sorted(out)


class SupabaseClient:
    """PostgreSQL client for image_tags table."""

    def __init__(self, database_uri: str | None = None):
        self._uri = database_uri or DATABASE_URI
        if not self._uri:
            raise ValueError("DATABASE_URI is required for SupabaseClient")

    def _conn(self, retries: int = 3, delay: float = 1.0):
        """Connect with retries; app continues without DB if connection fails (Phase 6)."""
        last_error = None
        for attempt in range(retries):
            try:
                return psycopg2.connect(self._uri)
            except Exception as e:
                last_error = e
                logger.warning("DB connection attempt %s/%s failed: %s", attempt + 1, retries, e)
                if attempt < retries - 1:
                    time.sleep(delay)
        raise last_error

    def upsert_tag_record(
        self,
        image_id: str,
        tag_record: dict,
        image_url: str | None = None,
        needs_review: bool = False,
        processing_status: str = "complete",
    ) -> None:
        """Insert or update a row in image_tags."""
        search_index = build_search_index(tag_record)
        tag_record_json = json.dumps(tag_record)
        conn = self._conn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO image_tags (image_id, tag_record, search_index, image_url, needs_review, processing_status, updated_at)
                    VALUES (%s, %s::jsonb, %s, %s, %s, %s, NOW())
                    ON CONFLICT (image_id) DO UPDATE SET
                      tag_record = EXCLUDED.tag_record,
                      search_index = EXCLUDED.search_index,
                      image_url = EXCLUDED.image_url,
                      needs_review = EXCLUDED.needs_review,
                      processing_status = EXCLUDED.processing_status,
                      updated_at = NOW()
                    """,
                    (image_id, tag_record_json, search_index, image_url, needs_review, processing_status),
                )
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.exception("upsert_tag_record failed: %s", e)
            raise
        finally:
            conn.close()

    def get_tag_record(self, image_id: str) -> dict | None:
        """Return one row as dict or None."""
        conn = self._conn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT image_id, tag_record, search_index, image_url, needs_review, processing_status, created_at, updated_at FROM image_tags WHERE image_id = %s",
                    (image_id,),
                )
                row = cur.fetchone()
                if row is None:
                    return None
                d = dict(row)
                return d
        finally:
            conn.close()

    def list_tag_images(self, limit: int = 20, offset: int = 0) -> list[dict]:
        """Return rows ordered by created_at DESC."""
        conn = self._conn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT image_id, tag_record, search_index, image_url, needs_review, processing_status, created_at, updated_at FROM image_tags ORDER BY created_at DESC LIMIT %s OFFSET %s",
                    (limit, offset),
                )
                rows = cur.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def search_images_filtered(self, filters: dict, limit: int = 50) -> list[dict]:
        """Return rows where search_index contains ALL specified values (AND logic)."""
        flat_values: list[str] = []
        for values in filters.values():
            if isinstance(values, list):
                for v in values:
                    if isinstance(v, str) and v.strip():
                        flat_values.append(v.strip())
            elif isinstance(values, str) and values.strip():
                flat_values.append(values.strip())
        if not flat_values:
            return self.list_tag_images(limit=limit, offset=0)
        conn = self._conn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT image_id, tag_record, search_index, image_url, needs_review, processing_status, created_at, updated_at FROM image_tags WHERE search_index @> %s::text[] ORDER BY created_at DESC LIMIT %s",
                    (flat_values, limit),
                )
                rows = cur.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def get_available_filter_values(self, filters: dict) -> dict:
        """From filtered results, collect unique tag values per category for cascading filters."""
        rows = self.search_images_filtered(filters, limit=500)
        categories: dict[str, set[str]] = {}
        for row in rows:
            record = row.get("tag_record")
            if not isinstance(record, dict):
                continue
            for key in ("season", "theme", "design_elements", "occasion", "mood"):
                val = record.get(key)
                if isinstance(val, list):
                    categories.setdefault(key, set()).update(v for v in val if isinstance(v, str))
            for key in ("objects", "dominant_colors"):
                val = record.get(key)
                if isinstance(val, list):
                    for item in val:
                        if isinstance(item, dict):
                            if item.get("parent"):
                                categories.setdefault(key, set()).add(item["parent"])
                            if item.get("child"):
                                categories.setdefault(key, set()).add(item["child"])
            pt = record.get("product_type")
            if isinstance(pt, dict):
                if pt.get("parent"):
                    categories.setdefault("product_type", set()).add(pt["parent"])
                if pt.get("child"):
                    categories.setdefault("product_type", set()).add(pt["child"])
        return {k: sorted(s) for k, s in categories.items()}


def get_client() -> SupabaseClient | None:
    """Return a SupabaseClient if DATABASE_URI is set, else None."""
    if not SUPABASE_ENABLED:
        return None
    try:
        return SupabaseClient()
    except Exception as e:
        logger.warning("Supabase client not available: %s", e)
        return None
