import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from mcc.cognitive.adapters import OpenFOAMAdapter, LAMMPSAdapter

base_workdir = os.path.join(PROJECT_ROOT, "sim_jobs")
os.makedirs(base_workdir, exist_ok=True)

foam = OpenFOAMAdapter()
lj = LAMMPSAdapter()

foam_job = foam.create_job(job_id="foam-001", workdir=base_workdir, inputs={"case": "pipe_flow"})
lj_job = lj.create_job(job_id="lmp-001", workdir=base_workdir, inputs={"material": "Al"})

print("OpenFOAM job:", foam_job)
print("LAMMPS job:", lj_job)
