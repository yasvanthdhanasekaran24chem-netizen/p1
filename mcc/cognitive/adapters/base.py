from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional


JobStatus = Literal["queued", "running", "completed", "failed"]


@dataclass
class SimulationJob:
    job_id: str
    backend: str
    workdir: str
    inputs: Dict[str, object] = field(default_factory=dict)
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass
class SimulationResult:
    job_id: str
    status: JobStatus
    metrics: Dict[str, float] = field(default_factory=dict)
    artifacts: Dict[str, str] = field(default_factory=dict)
    logs: List[str] = field(default_factory=list)
    error: Optional[str] = None


class SimulationAdapter(ABC):
    """Unified adapter contract for all simulation backends."""

    @abstractmethod
    def backend_name(self) -> str:
        pass

    @abstractmethod
    def create_job(self, *, job_id: str, workdir: str, inputs: Dict[str, object]) -> SimulationJob:
        pass

    @abstractmethod
    def run(self, job: SimulationJob) -> SimulationResult:
        pass

    @abstractmethod
    def parse_results(self, job: SimulationJob) -> SimulationResult:
        pass
