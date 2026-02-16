from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict

from .base import SimulationAdapter, SimulationJob, SimulationResult
from .parsers import parse_openfoam_metrics


class OpenFOAMAdapter(SimulationAdapter):
    """OpenFOAM adapter with basic runtime wiring.

    Expected case layout in job dir:
    - Allrun (bash script)
    - optional metrics.json produced by post-processing
    """

    def backend_name(self) -> str:
        return "openfoam"

    def create_job(self, *, job_id: str, workdir: str, inputs: Dict[str, object]) -> SimulationJob:
        job_dir = Path(workdir) / job_id
        job_dir.mkdir(parents=True, exist_ok=True)

        (job_dir / "job_inputs.json").write_text(json.dumps(inputs, indent=2), encoding="utf-8")

        allrun = job_dir / "Allrun"
        if not allrun.exists():
            allrun.write_text(
                "#!/bin/bash\n"
                "set -e\n"
                "# Example OpenFOAM pipeline\n"
                "# blockMesh\n"
                "# snappyHexMesh -overwrite\n"
                "# simpleFoam\n",
                encoding="utf-8",
            )

        return SimulationJob(job_id=job_id, backend=self.backend_name(), workdir=str(job_dir), inputs=inputs)

    def run(self, job: SimulationJob) -> SimulationResult:
        job_dir = Path(job.workdir)
        metrics_file = job_dir / "metrics.json"
        if metrics_file.exists():
            return self.parse_results(job)

        allrun = job_dir / "Allrun"
        if not allrun.exists():
            return SimulationResult(job_id=job.job_id, status="failed", error="Allrun not found")

        shell = shutil.which("bash") or shutil.which("sh")
        wsl = shutil.which("wsl")
        wsl_distro = os.environ.get("P1_WSL_DISTRO", "Ubuntu")

        if shell is not None:
            proc = subprocess.run(
                [shell, str(allrun)],
                cwd=str(job_dir),
                capture_output=True,
                text=True,
                env=os.environ.copy(),
            )
        elif wsl is not None:
            win_path = str(job_dir).replace("\\", "/")
            if ":" in win_path:
                drive = win_path[0].lower()
                tail = win_path[2:]
                wsl_dir = f"/mnt/{drive}{tail}"
            else:
                wsl_dir = win_path
            cmdline = f"cd '{wsl_dir}' && bash ./Allrun"
            proc = subprocess.run(
                [wsl, "-d", wsl_distro, "bash", "-lc", cmdline],
                capture_output=True,
                text=True,
                env=os.environ.copy(),
            )
        else:
            return SimulationResult(
                job_id=job.job_id,
                status="failed",
                error="No bash/sh or wsl found for OpenFOAM Allrun execution.",
                logs=["Install WSL/Git Bash or provide precomputed metrics.json"],
            )

        logs = []
        if proc.stdout:
            logs.append(proc.stdout[-4000:])
        if proc.stderr:
            logs.append(proc.stderr[-4000:])

        if proc.returncode != 0:
            return SimulationResult(
                job_id=job.job_id,
                status="failed",
                error=f"Allrun failed with code {proc.returncode}",
                logs=logs,
            )

        if metrics_file.exists():
            parsed = self.parse_results(job)
            parsed.logs.extend(logs)
            return parsed

        extracted = parse_openfoam_metrics("\n".join(logs))
        if extracted:
            metrics_file.write_text(json.dumps({"metrics": extracted}, indent=2), encoding="utf-8")
            parsed = self.parse_results(job)
            parsed.logs.extend(logs)
            parsed.logs.append("Auto-extracted metrics from OpenFOAM logs")
            return parsed

        return SimulationResult(
            job_id=job.job_id,
            status="failed",
            error="Allrun completed but metrics.json not found.",
            logs=logs,
        )

    def parse_results(self, job: SimulationJob) -> SimulationResult:
        metrics_file = Path(job.workdir) / "metrics.json"
        if not metrics_file.exists():
            return SimulationResult(job_id=job.job_id, status="failed", error="metrics.json not found")

        data = json.loads(metrics_file.read_text(encoding="utf-8"))
        metrics = {k: float(v) for k, v in data.get("metrics", {}).items()}

        return SimulationResult(
            job_id=job.job_id,
            status="completed",
            metrics=metrics,
            artifacts={"workdir": job.workdir},
            logs=["Parsed OpenFOAM metrics.json"],
        )
