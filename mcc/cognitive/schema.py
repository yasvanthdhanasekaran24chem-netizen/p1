from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional

GoalDirection = Literal["minimize", "maximize"]


@dataclass
class ConstraintSpec:
    name: str
    kind: Literal["range", "lte", "gte", "eq"]
    field: str
    low: Optional[float] = None
    high: Optional[float] = None
    value: Optional[float] = None


@dataclass
class ObjectiveSpec:
    name: str
    direction: GoalDirection
    weight: float = 1.0


@dataclass
class ExperimentSpec:
    experiment_id: str
    domain: str
    parameters: Dict[str, float]
    objectives: List[ObjectiveSpec] = field(default_factory=list)
    constraints: List[ConstraintSpec] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass
class RunResult:
    experiment_id: str
    status: Literal["ok", "failed", "infeasible"]
    parameters: Dict[str, float]
    outputs: Dict[str, float]
    score: Optional[float] = None
    notes: List[str] = field(default_factory=list)
