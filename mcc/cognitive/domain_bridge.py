from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from mcc.core.domain_adapter import DomainAdapter

from .schema import ConstraintSpec


@dataclass
class DomainSimulationBridge:
    """Bridge cognitive engine to existing mcc.core domain adapters."""

    domain: DomainAdapter

    def simulate(self, params: Dict[str, float]) -> Dict[str, float]:
        candidate = {"params": dict(params)}
        return self.domain.simulate(candidate)

    def suggested_constraints(self) -> List[ConstraintSpec]:
        # Domain constraints in core are procedural functions; keep these as metadata hooks.
        # Hard checks still run in `validate_with_domain_constraints` below.
        return []

    def validate_with_domain_constraints(self, params: Dict[str, float], outputs: Dict[str, float]) -> bool:
        candidate = {"params": dict(params)}
        for fn in self.domain.constraints():
            if not fn(candidate, outputs):
                return False
        return True
