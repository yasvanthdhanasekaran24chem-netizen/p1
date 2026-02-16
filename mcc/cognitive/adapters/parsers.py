from __future__ import annotations

import re
from typing import Dict


def parse_openfoam_metrics(text: str) -> Dict[str, float]:
    metrics: Dict[str, float] = {}

    # Typical lines: "smoothSolver:  Solving for Ux, Initial residual = ..., Final residual = 1.2e-06"
    residuals = re.findall(r"Final residual\s*=\s*([0-9eE+\-.]+)", text)
    if residuals:
        vals = [float(x) for x in residuals]
        metrics["residual_final_last"] = vals[-1]
        metrics["residual_final_mean"] = sum(vals) / len(vals)

    # Time/iteration info
    iters = re.findall(r"Time\s*=\s*([0-9eE+\-.]+)", text)
    if iters:
        metrics["time_last"] = float(iters[-1])

    # Optional aerodynamic coefficients if present in logs
    m = re.findall(r"\bCl\b\s*=\s*([0-9eE+\-.]+)", text)
    if m:
        metrics["Cl_last"] = float(m[-1])
    m = re.findall(r"\bCd\b\s*=\s*([0-9eE+\-.]+)", text)
    if m:
        metrics["Cd_last"] = float(m[-1])

    return metrics


def parse_lammps_metrics(text: str) -> Dict[str, float]:
    metrics: Dict[str, float] = {}

    # Capture final thermo line-like numbers if available
    # Very generic fallback for values named in output
    pe = re.findall(r"\bPotEng\b\s*=\s*([0-9eE+\-.]+)", text)
    if pe:
        metrics["PotEng_last"] = float(pe[-1])

    temp = re.findall(r"\bTemp\b\s*=\s*([0-9eE+\-.]+)", text)
    if temp:
        metrics["Temp_last"] = float(temp[-1])

    press = re.findall(r"\bPress\b\s*=\s*([0-9eE+\-.]+)", text)
    if press:
        metrics["Press_last"] = float(press[-1])

    return metrics
