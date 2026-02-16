from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from .adapters import SimulationJob, SimulationResult


class JobStore:
    def __init__(self, db_path: str):
        self.db_path = str(Path(db_path))
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _conn(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._conn() as c:
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY,
                    backend TEXT NOT NULL,
                    workdir TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS results (
                    job_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS queue (
                    job_id TEXT PRIMARY KEY,
                    state TEXT NOT NULL,
                    error TEXT,
                    attempt_count INTEGER DEFAULT 0,
                    max_attempts INTEGER DEFAULT 1,
                    enqueued_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    started_at TEXT,
                    finished_at TEXT
                )
                """
            )
            # Backward-compatible migrations for existing DBs
            cols = [r[1] for r in c.execute("PRAGMA table_info(queue)").fetchall()]
            if "attempt_count" not in cols:
                c.execute("ALTER TABLE queue ADD COLUMN attempt_count INTEGER DEFAULT 0")
            if "max_attempts" not in cols:
                c.execute("ALTER TABLE queue ADD COLUMN max_attempts INTEGER DEFAULT 1")

    def upsert_job(self, job: SimulationJob):
        payload = json.dumps(asdict(job), ensure_ascii=False)
        with self._conn() as c:
            c.execute(
                """
                INSERT INTO jobs(job_id, backend, workdir, payload_json)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(job_id) DO UPDATE SET
                  backend=excluded.backend,
                  workdir=excluded.workdir,
                  payload_json=excluded.payload_json
                """,
                (job.job_id, job.backend, job.workdir, payload),
            )

    def upsert_result(self, result: SimulationResult):
        payload = json.dumps(asdict(result), ensure_ascii=False)
        with self._conn() as c:
            c.execute(
                """
                INSERT INTO results(job_id, status, payload_json, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(job_id) DO UPDATE SET
                  status=excluded.status,
                  payload_json=excluded.payload_json,
                  updated_at=CURRENT_TIMESTAMP
                """,
                (result.job_id, result.status, payload),
            )

    def get_job(self, job_id: str) -> Optional[SimulationJob]:
        with self._conn() as c:
            row = c.execute("SELECT payload_json FROM jobs WHERE job_id=?", (job_id,)).fetchone()
        if not row:
            return None
        return SimulationJob(**json.loads(row[0]))

    def get_result(self, job_id: str) -> Optional[SimulationResult]:
        with self._conn() as c:
            row = c.execute("SELECT payload_json FROM results WHERE job_id=?", (job_id,)).fetchone()
        if not row:
            return None
        return SimulationResult(**json.loads(row[0]))

    def list_jobs(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._conn() as c:
            rows = c.execute(
                """
                SELECT j.job_id, j.backend, j.created_at, r.status, r.updated_at
                FROM jobs j
                LEFT JOIN results r ON r.job_id = j.job_id
                ORDER BY j.created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        out = []
        for job_id, backend, created_at, status, updated_at in rows:
            out.append(
                {
                    "job_id": job_id,
                    "backend": backend,
                    "created_at": created_at,
                    "status": status or "queued",
                    "updated_at": updated_at,
                }
            )
        return out

    def enqueue(self, job_id: str, max_attempts: int = 1):
        with self._conn() as c:
            c.execute(
                """
                INSERT INTO queue(job_id, state, error, attempt_count, max_attempts, enqueued_at, started_at, finished_at)
                VALUES (?, 'queued', NULL, 0, ?, CURRENT_TIMESTAMP, NULL, NULL)
                ON CONFLICT(job_id) DO UPDATE SET
                  state='queued',
                  error=NULL,
                  max_attempts=excluded.max_attempts,
                  enqueued_at=CURRENT_TIMESTAMP,
                  started_at=NULL,
                  finished_at=NULL
                """,
                (job_id, max(1, int(max_attempts))),
            )

    def start_job(self, job_id: str):
        with self._conn() as c:
            c.execute(
                """
                UPDATE queue
                SET state='running', started_at=CURRENT_TIMESTAMP, error=NULL, attempt_count=attempt_count+1
                WHERE job_id=?
                """,
                (job_id,),
            )

    def finish_job(self, job_id: str, state: str, error: str | None = None):
        with self._conn() as c:
            c.execute(
                """
                UPDATE queue
                SET state=?, error=?, finished_at=CURRENT_TIMESTAMP
                WHERE job_id=?
                """,
                (state, error, job_id),
            )

    def should_retry(self, job_id: str) -> bool:
        with self._conn() as c:
            row = c.execute(
                "SELECT attempt_count, max_attempts FROM queue WHERE job_id=?",
                (job_id,),
            ).fetchone()
        if not row:
            return False
        attempt_count, max_attempts = row
        return int(attempt_count) < int(max_attempts)

    def requeue_for_retry(self, job_id: str, error: str | None = None):
        with self._conn() as c:
            c.execute(
                """
                UPDATE queue
                SET state='queued', error=?, started_at=NULL, finished_at=NULL, enqueued_at=CURRENT_TIMESTAMP
                WHERE job_id=?
                """,
                (error, job_id),
            )

    def cancel(self, job_id: str, reason: str | None = None):
        with self._conn() as c:
            c.execute(
                """
                UPDATE queue
                SET state='cancelled', error=?, finished_at=CURRENT_TIMESTAMP
                WHERE job_id=?
                """,
                (reason, job_id),
            )

    def replay_dead(self, job_id: str, max_attempts: int = 1):
        with self._conn() as c:
            c.execute(
                """
                UPDATE queue
                SET state='queued',
                    error=NULL,
                    attempt_count=0,
                    max_attempts=?,
                    enqueued_at=CURRENT_TIMESTAMP,
                    started_at=NULL,
                    finished_at=NULL
                WHERE job_id=? AND state='dead'
                """,
                (max(1, int(max_attempts)), job_id),
            )

    def next_queued_job_id(self) -> Optional[str]:
        with self._conn() as c:
            row = c.execute(
                """
                SELECT job_id FROM queue
                WHERE state='queued'
                ORDER BY enqueued_at ASC
                LIMIT 1
                """
            ).fetchone()
        return row[0] if row else None

    def queue_state(self, job_id: str) -> Optional[Dict[str, Any]]:
        with self._conn() as c:
            row = c.execute(
                """
                SELECT state, error, attempt_count, max_attempts, enqueued_at, started_at, finished_at
                FROM queue WHERE job_id=?
                """,
                (job_id,),
            ).fetchone()
        if not row:
            return None
        state, error, attempt_count, max_attempts, enqueued_at, started_at, finished_at = row
        return {
            "state": state,
            "error": error,
            "attempt_count": int(attempt_count or 0),
            "max_attempts": int(max_attempts or 1),
            "enqueued_at": enqueued_at,
            "started_at": started_at,
            "finished_at": finished_at,
        }

    def purge_finished(self, keep_latest: int = 200) -> int:
        with self._conn() as c:
            rows = c.execute(
                """
                SELECT job_id FROM queue
                WHERE state IN ('completed','failed','dead','cancelled')
                ORDER BY COALESCE(finished_at, enqueued_at) DESC
                """
            ).fetchall()
            to_delete = [r[0] for r in rows[keep_latest:]]
            for job_id in to_delete:
                c.execute("DELETE FROM queue WHERE job_id=?", (job_id,))
                c.execute("DELETE FROM results WHERE job_id=?", (job_id,))
                c.execute("DELETE FROM jobs WHERE job_id=?", (job_id,))
        return len(to_delete)

    def summary(self) -> Dict[str, Any]:
        with self._conn() as c:
            total = c.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
            by_status = c.execute(
                "SELECT status, COUNT(*) FROM results GROUP BY status"
            ).fetchall()
            q_by_state = c.execute(
                "SELECT state, COUNT(*) FROM queue GROUP BY state"
            ).fetchall()
        status_counts = {k: int(v) for k, v in by_status}
        queue_counts = {k: int(v) for k, v in q_by_state}
        return {"total_jobs": int(total), "status_counts": status_counts, "queue_counts": queue_counts}
