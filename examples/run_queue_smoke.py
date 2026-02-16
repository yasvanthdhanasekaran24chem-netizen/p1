import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from mcc.cognitive.service import CognitiveSimulationService

svc = CognitiveSimulationService(base_workdir=os.path.join(PROJECT_ROOT, "sim_jobs"))

j = svc.create_job("openfoam", {"case": "pipe_flow_queue"})
job_id = j["job_id"]
print("created:", job_id)

print("enqueue:", svc.enqueue_job(job_id))
print("queue_before:", svc.queue_status(job_id))

step = svc.run_next_queued()
print("worker_step:", step)

print("queue_after:", svc.queue_status(job_id))
print("job:", svc.get_job(job_id))
