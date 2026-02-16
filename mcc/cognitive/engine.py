from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Literal

from .memory import CognitiveMemoryStore
from .pareto import pareto_front
from .planner import DesignSpace, ExperimentPlanner
from .schema import ConstraintSpec, ObjectiveSpec, RunResult

SimulatorFn = Callable[[Dict[str, float]], Dict[str, float]]
PenaltyMode = Literal["discard", "soft"]


@dataclass
class CognitiveEngine:
    domain: str
    planner: ExperimentPlanner
    memory: CognitiveMemoryStore
    simulator: SimulatorFn

    def run_iteration(
        self,
        *,
        design_space: DesignSpace,
        objectives: List[ObjectiveSpec],
        constraints: List[ConstraintSpec],
        n: int = 1,
        penalty_mode: PenaltyMode = "discard",
        penalty_value: float = 1e6,
    ) -> List[RunResult]:
        history = self.memory.load_all()
        specs = self.planner.propose(
            domain=self.domain,
            design_space=design_space,
            objectives=objectives,
            constraints=constraints,
            history=history,
            n=n,
        )

        results: List[RunResult] = []
        for spec in specs:
            outputs = self.simulator(spec.parameters)
            status = self._check_constraints(outputs, spec.constraints)

            if status == "ok":
                score = self._score(outputs, spec.objectives)
            elif penalty_mode == "soft":
                score = -abs(penalty_value)
            else:
                score = None

            notes = []
            if spec.metadata:
                planner_name = spec.metadata.get("planner")
                acq = spec.metadata.get("acquisition")
                if planner_name:
                    notes.append(f"planner={planner_name}")
                if acq:
                    notes.append(f"acquisition={acq}")

            result = RunResult(
                experiment_id=spec.experiment_id,
                status=status,
                parameters=dict(spec.parameters),
                outputs=outputs,
                score=score,
                notes=notes,
            )
            self.memory.append(result)
            results.append(result)

        return results

    def current_pareto_front(self, objectives: List[ObjectiveSpec]) -> List[RunResult]:
        history = self.memory.load_all()
        return pareto_front(history, objectives)

    @staticmethod
    def _score(outputs: Dict[str, float], objectives: List[ObjectiveSpec]) -> float:
        total = 0.0
        for obj in objectives:
            val = float(outputs.get(obj.name, 0.0))
            signed = val if obj.direction == "maximize" else -val
            total += obj.weight * signed
        return total

    @staticmethod
    def _check_constraints(outputs: Dict[str, float], constraints: List[ConstraintSpec]) -> str:
        for c in constraints:
            val = outputs.get(c.field)
            if val is None:
                return "failed"
            if c.kind == "range":
                if c.low is not None and val < c.low:
                    return "infeasible"
                if c.high is not None and val > c.high:
                    return "infeasible"
            elif c.kind == "lte" and c.value is not None and val > c.value:
                return "infeasible"
            elif c.kind == "gte" and c.value is not None and val < c.value:
                return "infeasible"
            elif c.kind == "eq" and c.value is not None and abs(val - c.value) > 1e-9:
                return "infeasible"
        return "ok"
