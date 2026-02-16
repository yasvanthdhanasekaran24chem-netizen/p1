import os
import tempfile

from mcc.cognitive import (
    BaselineGridPlanner,
    CognitiveEngine,
    CognitiveMemoryStore,
    ConstraintSpec,
    DesignSpace,
    ObjectiveSpec,
)


def toy_simulator(params):
    x = params["x"]
    return {"yield": 100 - (x - 2) ** 2, "energy": x**2}


def test_cognitive_engine_smoke():
    with tempfile.TemporaryDirectory() as td:
        memory_path = os.path.join(td, "mem.jsonl")

        engine = CognitiveEngine(
            domain="toy",
            planner=BaselineGridPlanner(),
            memory=CognitiveMemoryStore(path=memory_path),
            simulator=toy_simulator,
        )

        results = engine.run_iteration(
            design_space=DesignSpace(bounds={"x": (0.0, 4.0)}),
            objectives=[ObjectiveSpec(name="yield", direction="maximize", weight=1.0)],
            constraints=[ConstraintSpec(name="yield_floor", kind="gte", field="yield", value=50.0)],
            n=2,
        )

        assert len(results) == 2
        assert all(r.status in {"ok", "infeasible", "failed"} for r in results)
