from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any, Dict

from mcc.cognitive.service import CognitiveSimulationService


def create_service() -> CognitiveSimulationService:
    base_workdir = os.environ.get("P1_WORKDIR", str(Path(__file__).resolve().parents[1] / "sim_jobs"))
    return CognitiveSimulationService(base_workdir=base_workdir)


def create_app():
    try:
        from fastapi import Depends, FastAPI
    except Exception as e:  # pragma: no cover
        raise RuntimeError("FastAPI is not installed. Install fastapi+uvicorn to run API server.") from e

    from api.auth import require_api_key
    from api.errors import api_error
    from api.middleware import AuditLogMiddleware, RateLimitMiddleware

    service = create_service()
    app = FastAPI(
        title="Cognitive Simulation API",
        version="0.1.0",
        dependencies=[Depends(require_api_key)],
    )
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(AuditLogMiddleware)

    @app.post("/jobs")
    def create_job(payload: Dict[str, Any]):
        try:
            return service.create_job(backend=payload["backend"], inputs=payload.get("inputs", {}))
        except Exception as e:
            api_error(400, "CREATE_JOB_FAILED", "Could not create job", str(e))

    @app.post("/jobs/{job_id}/run")
    def run_job(job_id: str):
        try:
            return service.run_job(job_id)
        except KeyError as e:
            api_error(404, "JOB_NOT_FOUND", "Job not found", str(e))
        except Exception as e:
            api_error(400, "RUN_JOB_FAILED", "Could not run job", str(e))

    @app.post("/jobs/{job_id}/enqueue")
    def enqueue_job(job_id: str, max_attempts: int = 1):
        try:
            return service.enqueue_job(job_id, max_attempts=max_attempts)
        except KeyError as e:
            api_error(404, "JOB_NOT_FOUND", "Job not found", str(e))

    @app.post("/queue/run-next")
    def run_next_queued():
        return service.run_next_queued()

    @app.post("/queue/worker-step")
    def worker_step():
        return service.run_next_queued()

    @app.get("/queue/{job_id}")
    def queue_status(job_id: str):
        try:
            return service.queue_status(job_id)
        except KeyError as e:
            api_error(404, "QUEUE_NOT_FOUND", "Queue record not found", str(e))

    @app.post("/queue/{job_id}/cancel")
    def cancel_job(job_id: str, reason: str | None = None):
        try:
            return service.cancel_job(job_id, reason=reason)
        except KeyError as e:
            api_error(404, "QUEUE_NOT_FOUND", "Queue record not found", str(e))
        except ValueError as e:
            api_error(400, "CANCEL_FAILED", "Could not cancel job", str(e))

    @app.post("/queue/{job_id}/replay")
    def replay_dead_job(job_id: str, max_attempts: int = 1):
        try:
            return service.replay_dead_job(job_id, max_attempts=max_attempts)
        except KeyError as e:
            api_error(404, "QUEUE_NOT_FOUND", "Queue record not found", str(e))
        except ValueError as e:
            api_error(400, "REPLAY_FAILED", "Could not replay dead job", str(e))

    @app.post("/queue/purge")
    def purge_finished(keep_latest: int = 200):
        return service.purge_finished(keep_latest=keep_latest)

    @app.get("/jobs")
    def list_jobs(limit: int = 50):
        return service.list_jobs(limit=limit)

    @app.get("/jobs/{job_id}")
    def get_job(job_id: str):
        try:
            return service.get_job(job_id)
        except KeyError as e:
            api_error(404, "JOB_NOT_FOUND", "Job not found", str(e))

    @app.post("/experiments/suggest")
    def suggest(payload: Dict[str, Any]):
        try:
            return service.suggest_experiments(
                domain=payload["domain"],
                planner=payload.get("planner", "model_based"),
                design_space=payload["design_space"],
                objectives=payload["objectives"],
                constraints=payload.get("constraints", []),
                n=int(payload.get("n", 1)),
            )
        except Exception as e:
            api_error(400, "SUGGEST_FAILED", "Could not suggest experiments", str(e))

    @app.get("/health/live")
    def health_live():
        return {"status": "ok", "ts": int(time.time())}

    @app.get("/health/ready")
    def health_ready():
        try:
            # readiness = can touch summary and backend health without error
            s = service.summary()
            return {"status": "ready", "summary": s}
        except Exception as e:
            api_error(503, "NOT_READY", "Service not ready", str(e))

    @app.get("/health/backends")
    def backend_health():
        return service.backend_health()

    @app.get("/summary")
    def summary():
        return service.summary()

    @app.get("/config/effective")
    def effective_config():
        return {
            "auth": {
                "api_key_required": bool(os.environ.get("P1_API_KEY")),
            },
            "rate_limit": {
                "enabled": os.environ.get("P1_RATE_LIMIT_ENABLED", "1") != "0",
                "max": int(os.environ.get("P1_RATE_LIMIT_MAX", "60")),
                "window_sec": int(os.environ.get("P1_RATE_LIMIT_WINDOW_SEC", "60")),
            },
            "audit": {
                "enabled": os.environ.get("P1_AUDIT_LOG_ENABLED", "1") != "0",
                "path": os.environ.get("P1_AUDIT_LOG_PATH", str(Path(__file__).resolve().parents[1] / "sim_jobs" / "api_audit.jsonl")),
            },
            "workdir": os.environ.get("P1_WORKDIR", str(Path(__file__).resolve().parents[1] / "sim_jobs")),
        }

    return app


app = create_app()
