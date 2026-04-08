from __future__ import annotations

import logging
from typing import Any, Optional

from pyairtable import Api

from src.services.airtable.settings import AirtableSettings

logger = logging.getLogger(__name__)


def _escape_formula_value(value: str) -> str:
    return value.replace("\\", "\\\\").replace("'", "\\'")


class AirtableClient:
    def __init__(self, settings: AirtableSettings | None = None) -> None:
        self.settings = settings or AirtableSettings()
        self._api: Api | None = None
        self._table_ids: dict[str, str] = {}
        self._default_view_ids: dict[str, str] = {}
        if self.settings.api_key and self.settings.base_id:
            self._api = Api(self.settings.api_key)
            self._resolve_table_ids()

    def _resolve_table_ids(self) -> None:
        """Map table names -> table IDs and default view IDs.

        Priority: explicit IDs from env (AIRTABLE_PO_TABLE_ID, etc.), then Airtable
        metadata API. Env IDs don't require schema:read scope on the token.
        """
        s = self.settings
        if s.po_table_id:
            self._table_ids[s.po_table] = s.po_table_id
            if s.po_view_id:
                self._default_view_ids[s.po_table_id] = s.po_view_id
        if s.items_table_id:
            self._table_ids[s.items_table] = s.items_table_id
            if s.items_view_id:
                self._default_view_ids[s.items_table_id] = s.items_view_id

        if self._table_ids:
            logger.info("Airtable table IDs from env: %s", self._table_ids)
            logger.info("Airtable view IDs from env: %s", self._default_view_ids)
            return

        try:
            base = self._api.base(self.settings.base_id)
            for tbl in base.schema().tables:
                self._table_ids[tbl.name] = tbl.id
                views = getattr(tbl, "views", None)
                if views:
                    self._default_view_ids[tbl.id] = views[0].id
            if not self._default_view_ids:
                for tbl_name, tbl_id in self._table_ids.items():
                    try:
                        t = self._api.table(self.settings.base_id, tbl_id)
                        ts = t.schema()
                        if hasattr(ts, "views") and ts.views:
                            self._default_view_ids[tbl_id] = ts.views[0].id
                    except Exception:
                        pass
            logger.info("Airtable table IDs from API: %s", self._table_ids)
            logger.info("Airtable view IDs from API: %s", self._default_view_ids)
        except Exception as e:
            logger.warning("Could not resolve Airtable table IDs via API: %s", e)

    @property
    def enabled(self) -> bool:
        return self._api is not None

    def _po_table(self):
        if not self._api:
            raise RuntimeError("Airtable not configured")
        return self._api.table(self.settings.base_id, self.settings.po_table)

    def _items_table(self):
        if not self._api:
            raise RuntimeError("Airtable not configured")
        return self._api.table(self.settings.base_id, self.settings.items_table)

    def create_po_record(self, po_data: dict[str, Any]) -> str:
        rec = self._po_table().create(po_data)
        return str(rec["id"])

    def update_po_record(self, record_id: str, po_data: dict[str, Any]) -> str:
        rec = self._po_table().update(record_id, po_data)
        return str(rec["id"])

    def create_po_items(self, po_record_id: str, items: list[dict[str, Any]]) -> list[str]:
        ids: list[str] = []
        for item in items:
            fields = {**item, "Linked PO": [po_record_id]}
            rec = self._items_table().create(fields)
            ids.append(str(rec["id"]))
        return ids

    def find_po_by_number(self, po_number: str) -> Optional[dict[str, Any]]:
        if not self._api or not po_number:
            return None
        safe = _escape_formula_value(po_number.strip())
        formula = f"{{PO Number}}='{safe}'"
        try:
            return self._po_table().first(formula=formula)
        except Exception as e:
            logger.warning("Airtable find_po_by_number failed: %s", e)
            return None

    def upload_file_to_field(
        self,
        record_id: str,
        field_name: str,
        filename: str,
        content: bytes,
        content_type: str | None = None,
    ) -> None:
        """Upload bytes into an Airtable attachment-type field (pyairtable helper)."""
        if not self._api:
            raise RuntimeError("Airtable not configured")
        self._po_table().upload_attachment(
            record_id,
            field_name,
            filename,
            content=content,
            content_type=content_type,
        )

    def record_url(self, table_name: str, record_id: str) -> str:
        """Build a clickable Airtable web URL for a record.

        Format: https://airtable.com/{base_id}/{table_id}/{view_id}/{record_id}
        All segments must be IDs (appXXX, tblXXX, viwXXX, recXXX). Using a human
        table name like "Customer POs" produces a broken link.
        """
        base = self.settings.base_id
        if table_name.startswith("tbl"):
            table_id = table_name
        else:
            table_id = self._table_ids.get(table_name)
            if not table_id:
                logger.warning(
                    "record_url: no table ID for %r (resolved: %s); URL may be broken",
                    table_name, list(self._table_ids.keys()),
                )
                table_id = table_name
        view_id = self._default_view_ids.get(table_id)
        if view_id:
            return f"https://airtable.com/{base}/{table_id}/{view_id}/{record_id}"
        return f"https://airtable.com/{base}/{table_id}/{record_id}"
