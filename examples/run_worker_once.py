import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from mcc.cognitive.worker import run_worker

run_worker(base_workdir=os.path.join(PROJECT_ROOT, "sim_jobs"), once=True)
