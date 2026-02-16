import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from mcc.cognitive.service import CognitiveSimulationService

svc = CognitiveSimulationService(base_workdir=os.path.join(PROJECT_ROOT, "sim_jobs"))

# create + enqueue then cancel
j1 = svc.create_job("lammps", {"material": "ops-demo"})
job1 = j1["job_id"]
svc.enqueue_job(job1, max_attempts=1)
print("cancel:", svc.cancel_job(job1, reason="ops smoke"))

# create dead job then replay
j2 = svc.create_job("openfoam", {"case": "ops-dead-replay"})
job2 = j2["job_id"]
svc.enqueue_job(job2, max_attempts=1)
print("worker:", svc.run_next_queued())
print("q_before_replay:", svc.queue_status(job2))
print("replay:", svc.replay_dead_job(job2, max_attempts=2))

# purge
print("purge:", svc.purge_finished(keep_latest=5))
