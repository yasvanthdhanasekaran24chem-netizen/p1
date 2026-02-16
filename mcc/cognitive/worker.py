from __future__ import annotations

import argparse
import os
import time
from pathlib import Path

from .service import CognitiveSimulationService


def run_worker(base_workdir: str, interval_seconds: float = 2.0, once: bool = False):
    svc = CognitiveSimulationService(base_workdir=base_workdir)

    if once:
        out = svc.run_next_queued()
        print(out)
        return

    print(f"[worker] starting queue worker | workdir={base_workdir} | interval={interval_seconds}s")
    while True:
        out = svc.run_next_queued()
        if out.get("status") != "idle":
            print(f"[worker] {out}")
        time.sleep(interval_seconds)


def main():
    parser = argparse.ArgumentParser(description="Cognitive queue worker")
    parser.add_argument("--workdir", default=os.environ.get("P1_WORKDIR", str(Path(__file__).resolve().parents[2] / "sim_jobs")))
    parser.add_argument("--interval", type=float, default=2.0)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()

    run_worker(base_workdir=args.workdir, interval_seconds=args.interval, once=args.once)


if __name__ == "__main__":
    main()
