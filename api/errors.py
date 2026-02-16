from __future__ import annotations

from fastapi import HTTPException


def api_error(status_code: int, code: str, message: str, details: str | None = None):
    payload = {
        "error": {
            "code": code,
            "message": message,
        }
    }
    if details:
        payload["error"]["details"] = details
    raise HTTPException(status_code=status_code, detail=payload)
