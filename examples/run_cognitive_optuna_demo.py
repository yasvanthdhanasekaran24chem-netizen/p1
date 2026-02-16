import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from mcc.cognitive import (
    CognitiveEngine,
    CognitiveMemoryStore,
    ConstraintSpec,
    DesignSpace,
    ObjectiveSpec,
    OptunaTPEPlanner,
)


def toy_simulator(params):
    x = params["x"]
    y = params["y"]
    yield_ = max(0.0, 100 - (x - 3) ** 2 - (y - 2) ** 2)
    energy = x**2 + 0.5 * y**2
    return {"yield": float(yield_), "energy": float(energy)}


engine = CognitiveEngine(
    domain="toy_process",
    planner=OptunaTPEPlanner(seed=11),
    memory=CognitiveMemoryStore(path=os.path.join(PROJECT_ROOT, "cognitive_memory_optuna.jsonl")),
    simulator=toy_simulator,
)

results = engine.run_iteration(
    design_space=DesignSpace(bounds={"x": (0.0, 8.0), "y": (0.0, 6.0)}),
    objectives=[
        ObjectiveSpec(name="yield", direction="maximize", weight=0.8),
        ObjectiveSpec(name="energy", direction="minimize", weight=0.2),
    ],
    constraints=[ConstraintSpec(name="yield_floor", kind="gte", field="yield", value=40.0)],
    n=3,
)

for r in results:
    print(r)
