from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict

from .base import SimulationAdapter, SimulationJob, SimulationResult


class QuantumEspressoAdapter(SimulationAdapter):
    """Quantum ESPRESSO adapter skeleton (pw.x).

    Runtime command via `QE_CMD` (default: pw.x).
    """

    def backend_name(self) -> str:
        return "quantum_espresso"

    def create_job(self, *, job_id: str, workdir: str, inputs: Dict[str, object]) -> SimulationJob:
        job_dir = Path(workdir) / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        (job_dir / "job_inputs.json").write_text(json.dumps(inputs, indent=2), encoding="utf-8")

        infile = job_dir / "qe.in"
        if not infile.exists():
            infile.write_text("&control\n calculation='scf'\n/\n", encoding="utf-8")

        return SimulationJob(job_id=job_id, backend=self.backend_name(), workdir=str(job_dir), inputs=inputs)

    def run(self, job: SimulationJob) -> SimulationResult:
        job_dir = Path(job.workdir)
        metrics_file = job_dir / "metrics.json"
        if metrics_file.exists():
            return self.parse_results(job)

        cmd = os.environ.get("QE_CMD", "pw.x")
        exe = shutil.which(cmd)
        wsl = shutil.which("wsl")
        wsl_distro = os.environ.get("P1_WSL_DISTRO", "Ubuntu")

        if exe is not None:
            proc = subprocess.run([exe, "-in", "qe.in"], cwd=str(job_dir), capture_output=True, text=True)
        elif wsl is not None:
            win_path = str(job_dir).replace('\\', '/')
            if ':' in win_path:
                drive = win_path[0].lower()
                tail = win_path[2:]
                wsl_dir = f"/mnt/{drive}{tail}"
            else:
                wsl_dir = win_path
            cmdline = f"cd '{wsl_dir}' && {cmd} -in qe.in"
            proc = subprocess.run([wsl, "-d", wsl_distro, "bash", "-lc", cmdline], capture_output=True, text=True)
        else:
            return SimulationResult(job_id=job.job_id, status="failed", error=f"QE executable not found: {cmd}")
        logs = [x for x in [proc.stdout[-4000:] if proc.stdout else "", proc.stderr[-4000:] if proc.stderr else ""] if x]

        if proc.returncode != 0:
            return SimulationResult(job_id=job.job_id, status="failed", error=f"QE failed with code {proc.returncode}", logs=logs)

        if metrics_file.exists():
            parsed = self.parse_results(job)
            parsed.logs.extend(logs)
            return parsed

        return SimulationResult(job_id=job.job_id, status="failed", error="QE completed but metrics.json not found.", logs=logs)

    def parse_results(self, job: SimulationJob) -> SimulationResult:
        metrics_file = Path(job.workdir) / "metrics.json"
        if not metrics_file.exists():
            return SimulationResult(job_id=job.job_id, status="failed", error="metrics.json not found")
        data = json.loads(metrics_file.read_text(encoding="utf-8"))
        metrics = {k: float(v) for k, v in data.get("metrics", {}).items()}
        return SimulationResult(job_id=job.job_id, status="completed", metrics=metrics, artifacts={"workdir": job.workdir})
