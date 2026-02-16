import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from mcc.cognitive import (
    CognitiveEngine,
    CognitiveMemoryStore,
    DesignSpace,
    DomainSimulationBridge,
    ModelBasedPlanner,
    ObjectiveSpec,
)
from mcc.core.reaction_stoichiometry_domain import ReactionStoichiometryDomain


base_domain = ReactionStoichiometryDomain()
bridge = DomainSimulationBridge(base_domain)


def simulator(params):
    # include fixed known feed + planned design vars
    merged = {"FA0": 100.0, **params}
    out = bridge.simulate(merged)
    if not bridge.validate_with_domain_constraints(merged, out):
        # mimic failure signature when domain constraints reject
        return {**out, "conversion": -1.0}
    return out


engine = CognitiveEngine(
    domain="reaction_stoichiometry",
    planner=ModelBasedPlanner(acquisition="ucb", random_candidates=100),
    memory=CognitiveMemoryStore(path=os.path.join(PROJECT_ROOT, "reaction_cognitive_memory.jsonl")),
    simulator=simulator,
)

objectives = [
    ObjectiveSpec(name="conversion", direction="maximize", weight=0.6),
    ObjectiveSpec(name="selectivity", direction="maximize", weight=0.4),
]

results = engine.run_iteration(
    design_space=DesignSpace(bounds={"xi1": (0.0, 90.0), "xi2": (0.0, 90.0)}),
    objectives=objectives,
    constraints=[],
    n=5,
)

print("New results:")
for r in results:
    print(r)

front = engine.current_pareto_front(objectives)
print("\nPareto front size:", len(front))
for r in front[:5]:
    print(r.experiment_id, r.outputs.get("conversion"), r.outputs.get("selectivity"))
