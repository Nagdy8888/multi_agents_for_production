"""Base64 decode, temp files, and safe cleanup (GAS attachment handling)."""

from __future__ import annotations

import base64
import os
import tempfile


def b64decode_bytes(data_base64: str) -> bytes:
    """Decode webhook attachment payload (matches GAS `Utilities.base64Encode`)."""
    return base64.b64decode(data_base64, validate=False)


def write_temp_bytes(suffix: str, data: bytes) -> str:
    """Write bytes to a named temp file; caller must `unlink_silent(path)` when done."""
    tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    path = tmp.name
    tmp.write(data)
    tmp.close()
    return path


def unlink_silent(path: str | None) -> None:
    if path and os.path.exists(path):
        try:
            os.unlink(path)
        except OSError:
            pass
