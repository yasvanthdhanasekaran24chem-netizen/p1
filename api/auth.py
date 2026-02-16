from __future__ import annotations

import os
from fastapi import Header, HTTPException


def require_api_key(x_api_key: str | None = Header(default=None)):
    """Simple API key guard.

    Set env var `P1_API_KEY` to enable enforcement.
    If not set, auth is disabled (dev mode).
    """
    expected = os.environ.get("P1_API_KEY")
    if not expected:
        return
    if not x_api_key or x_api_key != expected:
        raise HTTPException(status_code=401, detail="Unauthorized: invalid or missing X-API-Key")
