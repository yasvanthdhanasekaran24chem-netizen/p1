from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict

from .base import SimulationAdapter, SimulationJob, SimulationResult


class CodeSaturneAdapter(SimulationAdapter):
    """Code_Saturne adapter skeleton.

    Runtime command via `CS_CMD` (default: code_saturne).
    """

    def backend_name(self) -> str:
        return "codesaturne"

    def create_job(self, *, job_id: str, workdir: str, inputs: Dict[str, object]) -> SimulationJob:
        job_dir = Path(workdir) / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        (job_dir / "job_inputs.json").write_text(json.dumps(inputs, indent=2), encoding="utf-8")
        return SimulationJob(job_id=job_id, backend=self.backend_name(), workdir=str(job_dir), inputs=inputs)

    def run(self, job: SimulationJob) -> SimulationResult:
        job_dir = Path(job.workdir)
        metrics_file = job_dir / "metrics.json"
        if metrics_file.exists():
            return self.parse_results(job)

        cmd = os.environ.get("CS_CMD", "code_saturne")
        exe = shutil.which(cmd)
        if exe is None:
            return SimulationResult(job_id=job.job_id, status="failed", error=f"Code_Saturne executable not found: {cmd}")

        proc = subprocess.run([exe, "run"], cwd=str(job_dir), capture_output=True, text=True)
        logs = [x for x in [proc.stdout[-4000:] if proc.stdout else "", proc.stderr[-4000:] if proc.stderr else ""] if x]

        if proc.returncode != 0:
            return SimulationResult(job_id=job.job_id, status="failed", error=f"Code_Saturne failed with code {proc.returncode}", logs=logs)

        if metrics_file.exists():
            parsed = self.parse_results(job)
            parsed.logs.extend(logs)
            return parsed

        return SimulationResult(job_id=job.job_id, status="failed", error="Code_Saturne completed but metrics.json not found.", logs=logs)

    def parse_results(self, job: SimulationJob) -> SimulationResult:
        metrics_file = Path(job.workdir) / "metrics.json"
        if not metrics_file.exists():
            return SimulationResult(job_id=job.job_id, status="failed", error="metrics.json not found")
        data = json.loads(metrics_file.read_text(encoding="utf-8"))
        metrics = {k: float(v) for k, v in data.get("metrics", {}).items()}
        return SimulationResult(job_id=job.job_id, status="completed", metrics=metrics, artifacts={"workdir": job.workdir})
