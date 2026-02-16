from __future__ import annotations

import os
import shutil
import uuid
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List

from .adapters import (
    CodeSaturneAdapter,
    LAMMPSAdapter,
    OpenFOAMAdapter,
    QuantumEspressoAdapter,
    SU2Adapter,
    SimulationAdapter,
    SimulationJob,
    SimulationResult,
)
from .engine import CognitiveEngine
from .job_store import JobStore
from .memory import CognitiveMemoryStore
from .planner import BaselineGridPlanner, DesignSpace, ModelBasedPlanner, OptunaTPEPlanner
from .schema import ConstraintSpec, ObjectiveSpec


class CognitiveSimulationService:
    def __init__(self, base_workdir: str):
        self.base_workdir = Path(base_workdir)
        self.base_workdir.mkdir(parents=True, exist_ok=True)

        self._jobs: Dict[str, SimulationJob] = {}
        self._results: Dict[str, SimulationResult] = {}
        self._store = JobStore(str(self.base_workdir / "service.db"))

        self._adapters: Dict[str, SimulationAdapter] = {
            "openfoam": OpenFOAMAdapter(),
            "lammps": LAMMPSAdapter(),
            "su2": SU2Adapter(),
            "codesaturne": CodeSaturneAdapter(),
            "quantum_espresso": QuantumEspressoAdapter(),
        }

    def create_job(self, backend: str, inputs: Dict[str, object]) -> Dict[str, object]:
        if backend not in self._adapters:
            raise ValueError(f"Unsupported backend: {backend}")

        job_id = f"job-{uuid.uuid4().hex[:8]}"
        adapter = self._adapters[backend]
        job = adapter.create_job(job_id=job_id, workdir=str(self.base_workdir), inputs=inputs)

        self._jobs[job_id] = job
        self._store.upsert_job(job)
        return asdict(job)

    def run_job(self, job_id: str) -> Dict[str, object]:
        job = self._jobs.get(job_id) or self._store.get_job(job_id)
        if not job:
            raise KeyError(f"Job not found: {job_id}")

        self._jobs[job_id] = job
        adapter = self._adapters[job.backend]
        result = adapter.run(job)
        self._results[job_id] = result
        self._store.upsert_result(result)
        return asdict(result)

    def get_job(self, job_id: str) -> Dict[str, object]:
        job = self._jobs.get(job_id) or self._store.get_job(job_id)
        if not job:
            raise KeyError(f"Job not found: {job_id}")

        result = self._results.get(job_id) or self._store.get_result(job_id)
        return {
            "job": asdict(job),
            "result": asdict(result) if result else None,
            "queue": self._store.queue_state(job_id),
        }

    def enqueue_job(self, job_id: str, max_attempts: int = 1) -> Dict[str, object]:
        job = self._jobs.get(job_id) or self._store.get_job(job_id)
        if not job:
            raise KeyError(f"Job not found: {job_id}")
        self._store.enqueue(job_id, max_attempts=max_attempts)
        return {"job_id": job_id, "queue": self._store.queue_state(job_id)}

    def run_next_queued(self) -> Dict[str, object]:
        job_id = self._store.next_queued_job_id()
        if not job_id:
            return {"status": "idle", "message": "No queued jobs."}

        self._store.start_job(job_id)
        try:
            result = self.run_job(job_id)
            ok = result.get("status") == "completed"
            if ok:
                self._store.finish_job(job_id, "completed", error=None)
                return {"status": "processed", "job_id": job_id, "result": result}

            # failed result path: retry if allowed, else dead-letter
            err = result.get("error") or "job failed"
            if self._store.should_retry(job_id):
                self._store.requeue_for_retry(job_id, error=err)
                return {"status": "requeued", "job_id": job_id, "result": result}

            self._store.finish_job(job_id, "dead", error=err)
            return {"status": "dead", "job_id": job_id, "result": result}
        except Exception as e:
            err = str(e)
            if self._store.should_retry(job_id):
                self._store.requeue_for_retry(job_id, error=err)
                return {"status": "requeued", "job_id": job_id, "error": err}
            self._store.finish_job(job_id, "dead", error=err)
            return {"status": "dead", "job_id": job_id, "error": err}

    def queue_status(self, job_id: str) -> Dict[str, object]:
        st = self._store.queue_state(job_id)
        if not st:
            raise KeyError(f"Queue record not found for job: {job_id}")
        return {"job_id": job_id, **st}

    def cancel_job(self, job_id: str, reason: str | None = None) -> Dict[str, object]:
        st = self._store.queue_state(job_id)
        if not st:
            raise KeyError(f"Queue record not found for job: {job_id}")
        if st.get("state") == "running":
            raise ValueError("Cannot cancel currently running job in this basic worker. Add cooperative cancellation token.")
        self._store.cancel(job_id, reason=reason or "cancelled by user")
        return {"job_id": job_id, "queue": self._store.queue_state(job_id)}

    def replay_dead_job(self, job_id: str, max_attempts: int = 1) -> Dict[str, object]:
        st = self._store.queue_state(job_id)
        if not st:
            raise KeyError(f"Queue record not found for job: {job_id}")
        if st.get("state") != "dead":
            raise ValueError("Only dead jobs can be replayed.")
        self._store.replay_dead(job_id, max_attempts=max_attempts)
        return {"job_id": job_id, "queue": self._store.queue_state(job_id)}

    def purge_finished(self, keep_latest: int = 200) -> Dict[str, object]:
        deleted = self._store.purge_finished(keep_latest=keep_latest)
        return {"deleted": deleted, "kept_latest": keep_latest}

    def list_jobs(self, limit: int = 50) -> List[Dict[str, object]]:
        return self._store.list_jobs(limit=limit)

    def summary(self) -> Dict[str, object]:
        return {
            **self._store.summary(),
            "backend_health": self.backend_health(),
        }

    def suggest_experiments(
        self,
        *,
        domain: str,
        planner: str,
        design_space: Dict[str, List[float]],
        objectives: List[Dict[str, object]],
        constraints: List[Dict[str, object]] | None = None,
        n: int = 1,
    ) -> List[Dict[str, object]]:
        planner_obj = self._build_planner(planner)
        memory_path = self.base_workdir / f"{domain}_service_memory.jsonl"

        # Placeholder simulator for API path; domain-specific engine can be plugged later
        def sim(params: Dict[str, float]) -> Dict[str, float]:
            x = float(params.get("x", 0.0))
            y = float(params.get("y", 0.0))
            return {
                "yield": max(0.0, 100.0 - (x - 3.0) ** 2 - (y - 2.0) ** 2),
                "energy": x * x + 0.5 * y * y,
            }

        engine = CognitiveEngine(
            domain=domain,
            planner=planner_obj,
            memory=CognitiveMemoryStore(path=memory_path),
            simulator=sim,
        )

        obj_specs = [ObjectiveSpec(**o) for o in objectives]
        c_specs = [ConstraintSpec(**c) for c in (constraints or [])]
        ds = DesignSpace(bounds={k: (float(v[0]), float(v[1])) for k, v in design_space.items()})

        runs = engine.run_iteration(
            design_space=ds,
            objectives=obj_specs,
            constraints=c_specs,
            n=n,
        )
        return [asdict(r) for r in runs]

    def backend_health(self) -> Dict[str, object]:
        return {
            "openfoam": {
                "bash": shutil.which("bash") is not None or shutil.which("sh") is not None,
                "wsl": shutil.which("wsl") is not None,
            },
            "lammps": {
                "cmd": os.environ.get("LAMMPS_CMD", "lmp"),
                "available": shutil.which(os.environ.get("LAMMPS_CMD", "lmp")) is not None or shutil.which("wsl") is not None,
            },
            "su2": {
                "cmd": os.environ.get("SU2_CMD", "SU2_CFD"),
                "available": shutil.which(os.environ.get("SU2_CMD", "SU2_CFD")) is not None,
            },
            "codesaturne": {
                "cmd": os.environ.get("CS_CMD", "code_saturne"),
                "available": shutil.which(os.environ.get("CS_CMD", "code_saturne")) is not None,
            },
            "quantum_espresso": {
                "cmd": os.environ.get("QE_CMD", "pw.x"),
                "available": shutil.which(os.environ.get("QE_CMD", "pw.x")) is not None or shutil.which("wsl") is not None,
            },
        }

    @staticmethod
    def _build_planner(name: str):
        if name == "baseline":
            return BaselineGridPlanner()
        if name == "model_based":
            return ModelBasedPlanner(acquisition="ei")
        if name == "optuna_tpe":
            return OptunaTPEPlanner()
        raise ValueError(f"Unsupported planner: {name}")
