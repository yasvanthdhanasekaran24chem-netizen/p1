from __future__ import annotations

import json
import os
import time
from collections import deque
from pathlib import Path
from typing import Deque, Dict, Tuple

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory sliding-window rate limiter.

    Controlled by env vars:
    - P1_RATE_LIMIT_ENABLED: "1"/"0" (default: 1)
    - P1_RATE_LIMIT_MAX: requests per window (default: 60)
    - P1_RATE_LIMIT_WINDOW_SEC: window size seconds (default: 60)
    """

    def __init__(self, app):
        super().__init__(app)
        self.enabled = os.environ.get("P1_RATE_LIMIT_ENABLED", "1") != "0"
        self.max_requests = int(os.environ.get("P1_RATE_LIMIT_MAX", "60"))
        self.window_sec = int(os.environ.get("P1_RATE_LIMIT_WINDOW_SEC", "60"))
        self.buckets: Dict[str, Deque[float]] = {}

    async def dispatch(self, request: Request, call_next):
        if not self.enabled:
            return await call_next(request)

        key = request.headers.get("X-API-Key") or request.client.host or "anonymous"
        now = time.time()
        q = self.buckets.setdefault(key, deque())

        # evict old timestamps
        cutoff = now - self.window_sec
        while q and q[0] < cutoff:
            q.popleft()

        if len(q) >= self.max_requests:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded",
                    "max_requests": self.max_requests,
                    "window_sec": self.window_sec,
                },
            )

        q.append(now)
        return await call_next(request)


class AuditLogMiddleware(BaseHTTPMiddleware):
    """Append basic request audit events to JSONL log file.

    Env vars:
    - P1_AUDIT_LOG_ENABLED: "1"/"0" (default: 1)
    - P1_AUDIT_LOG_PATH: file path (default: <repo>/sim_jobs/api_audit.jsonl)
    """

    def __init__(self, app):
        super().__init__(app)
        self.enabled = os.environ.get("P1_AUDIT_LOG_ENABLED", "1") != "0"
        default_path = str(Path(__file__).resolve().parents[1] / "sim_jobs" / "api_audit.jsonl")
        self.path = Path(os.environ.get("P1_AUDIT_LOG_PATH", default_path))
        self.path.parent.mkdir(parents=True, exist_ok=True)

    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        if self.enabled:
            event = {
                "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "latency_ms": int((time.time() - start) * 1000),
                "client": request.client.host if request.client else None,
                "has_api_key": bool(request.headers.get("X-API-Key")),
            }
            with self.path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(event, ensure_ascii=False) + "\n")
        return response
