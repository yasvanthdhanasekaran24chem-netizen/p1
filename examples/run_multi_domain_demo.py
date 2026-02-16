import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from mcc.core.problem_state import ProblemState
from mcc.core.mcc import MinimalCognitiveCore

ps = ProblemState(
    goal="combined_energy_and_mass",
    knowns={
        "inlet_flow": 100.0,
        "outlet_flow": 100.0,
        "mass_flow": 2.0,
        "h_in": 100.0,
        "h_out": 150.0,
        "heat_duty": 100.0
    },
    unknowns=[],
    assumptions=[
        "steady_state",
        "no_shaft_work",
        "no_ke_pe_change"
    ],
    criteria={"objectives": ["robustness"]}
)

mcc = MinimalCognitiveCore()
result = mcc.solve(ps)

print(result)
