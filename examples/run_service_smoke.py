import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from mcc.cognitive.service import CognitiveSimulationService

svc = CognitiveSimulationService(base_workdir=os.path.join(PROJECT_ROOT, "sim_jobs"))

job = svc.create_job("openfoam", {"case": "pipe_flow"})
print("job:", job)

job_id = job["job_id"]
res = svc.run_job(job_id)
print("run result:", res)

suggested = svc.suggest_experiments(
    domain="toy_process",
    planner="model_based",
    design_space={"x": [0.0, 8.0], "y": [0.0, 6.0]},
    objectives=[
        {"name": "yield", "direction": "maximize", "weight": 0.8},
        {"name": "energy", "direction": "minimize", "weight": 0.2},
    ],
    constraints=[{"name": "yield_floor", "kind": "gte", "field": "yield", "value": 40.0}],
    n=2,
)
print("suggested:", suggested)
