import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from mcc.core.problem_state import ProblemState
from mcc.core.mcc import MinimalCognitiveCore
from mcc.core.engineering_constraints import EngineeringConstraints

ps = ProblemState(
    goal="multi_objective_demo",
    knowns={"a": 2, "b": 5},
    unknowns=[],
    constraints=["non_negative"],
    assumptions=["steady_state"],
    criteria={
        "objectives": ["simplicity", "robustness"]
    }
)

rules = [
    EngineeringConstraints.non_negative_params
]

objective_weights = {
    "simplicity": 0.7,
    "robustness": 0.3
}

mcc = MinimalCognitiveCore(
    rules=rules,
    objective_weights=objective_weights
)

result = mcc.solve(ps)
print(result)
