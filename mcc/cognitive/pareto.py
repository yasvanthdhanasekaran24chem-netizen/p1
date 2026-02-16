from __future__ import annotations

from typing import Dict, List, Sequence

from .schema import ObjectiveSpec, RunResult


def objective_vector(outputs: Dict[str, float], objectives: Sequence[ObjectiveSpec]) -> Dict[str, float]:
    """Convert outputs to a canonical maximization vector for Pareto checks."""
    v: Dict[str, float] = {}
    for o in objectives:
        raw = float(outputs.get(o.name, 0.0))
        v[o.name] = raw if o.direction == "maximize" else -raw
    return v


def dominates(a: Dict[str, float], b: Dict[str, float]) -> bool:
    """True if a Pareto-dominates b (assuming all are maximize metrics)."""
    keys = set(a.keys()).intersection(b.keys())
    if not keys:
        return False
    ge_all = all(a[k] >= b[k] for k in keys)
    gt_any = any(a[k] > b[k] for k in keys)
    return ge_all and gt_any


def pareto_front(results: Sequence[RunResult], objectives: Sequence[ObjectiveSpec]) -> List[RunResult]:
    """Return non-dominated feasible results."""
    feasible = [r for r in results if r.status == "ok"]
    vectors = [objective_vector(r.outputs, objectives) for r in feasible]

    front: List[RunResult] = []
    for i, ri in enumerate(feasible):
        vi = vectors[i]
        dominated = False
        for j, vj in enumerate(vectors):
            if i == j:
                continue
            if dominates(vj, vi):
                dominated = True
                break
        if not dominated:
            front.append(ri)
    return front
