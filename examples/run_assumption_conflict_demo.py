import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from mcc.core.problem_state import ProblemState
from mcc.core.mcc import MinimalCognitiveCore

ps = ProblemState(
    goal="conflicting_assumptions_demo",
    knowns={
        "inlet_flow": 100.0,
        "outlet_flow": 100.0
    },
    unknowns=[],
    assumptions=[
        "steady_state",
        "dynamic"
    ],
    criteria={}
)

mcc = MinimalCognitiveCore()
result = mcc.solve(ps)
print(result)
