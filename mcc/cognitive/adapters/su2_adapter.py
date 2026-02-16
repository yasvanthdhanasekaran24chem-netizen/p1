from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict

from .base import SimulationAdapter, SimulationJob, SimulationResult


class SU2Adapter(SimulationAdapter):
    """SU2 adapter skeleton.

    Expects `config.cfg` in job dir (created as placeholder if missing).
    Runtime command can be set via `SU2_CMD` (default: SU2_CFD).
    """

    def backend_name(self) -> str:
        return "su2"

    def create_job(self, *, job_id: str, workdir: str, inputs: Dict[str, object]) -> SimulationJob:
        job_dir = Path(workdir) / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        (job_dir / "job_inputs.json").write_text(json.dumps(inputs, indent=2), encoding="utf-8")

        cfg = job_dir / "config.cfg"
        if not cfg.exists():
            cfg.write_text("% SU2 config placeholder\nSOLVER= RANS\n", encoding="utf-8")

        return SimulationJob(job_id=job_id, backend=self.backend_name(), workdir=str(job_dir), inputs=inputs)

    def run(self, job: SimulationJob) -> SimulationResult:
        job_dir = Path(job.workdir)
        metrics_file = job_dir / "metrics.json"
        if metrics_file.exists():
            return self.parse_results(job)

        cmd = os.environ.get("SU2_CMD", "SU2_CFD")
        exe = shutil.which(cmd)
        if exe is None:
            return SimulationResult(job_id=job.job_id, status="failed", error=f"SU2 executable not found: {cmd}")

        proc = subprocess.run([exe, "config.cfg"], cwd=str(job_dir), capture_output=True, text=True)
        logs = [x for x in [proc.stdout[-4000:] if proc.stdout else "", proc.stderr[-4000:] if proc.stderr else ""] if x]

        if proc.returncode != 0:
            return SimulationResult(job_id=job.job_id, status="failed", error=f"SU2 failed with code {proc.returncode}", logs=logs)

        if metrics_file.exists():
            parsed = self.parse_results(job)
            parsed.logs.extend(logs)
            return parsed

        return SimulationResult(job_id=job.job_id, status="failed", error="SU2 completed but metrics.json not found.", logs=logs)

    def parse_results(self, job: SimulationJob) -> SimulationResult:
        metrics_file = Path(job.workdir) / "metrics.json"
        if not metrics_file.exists():
            return SimulationResult(job_id=job.job_id, status="failed", error="metrics.json not found")
        data = json.loads(metrics_file.read_text(encoding="utf-8"))
        metrics = {k: float(v) for k, v in data.get("metrics", {}).items()}
        return SimulationResult(job_id=job.job_id, status="completed", metrics=metrics, artifacts={"workdir": job.workdir})
