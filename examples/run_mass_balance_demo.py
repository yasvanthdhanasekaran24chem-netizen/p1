import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from mcc.core.problem_state import ProblemState
from mcc.core.mcc import MinimalCognitiveCore
from mcc.core.engineering_constraints import EngineeringConstraints

ps = ProblemState(
    goal="steady_state_mass_balance",
    knowns={
        "inlet_flow": 100.0,
        "outlet_flow": 100.0
    },
    unknowns=[],
    constraints=["mass_conservation"],
    assumptions=["steady_state"],
    criteria={"objectives": ["robustness"]}
)

rules = [
    EngineeringConstraints.non_negative_params,
    EngineeringConstraints.steady_state_mass_balance
]

mcc = MinimalCognitiveCore(
    rules=rules,
    objective_weights={"robustness": 1.0}
)

result = mcc.solve(ps)
print(result)
