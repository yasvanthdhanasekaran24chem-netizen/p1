from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Dict, List, Literal, Sequence

from .schema import ConstraintSpec, ExperimentSpec, ObjectiveSpec, RunResult


@dataclass
class DesignSpace:
    bounds: Dict[str, tuple[float, float]]


AcquisitionKind = Literal["ucb", "ei", "thompson"]


class ExperimentPlanner:
    """Interface for cognitive planning.

    Future implementations:
    - BayesianOptimizerPlanner (BoTorch/Ax/Optuna backed)
    - ActiveLearningPlanner
    """

    def propose(
        self,
        *,
        domain: str,
        design_space: DesignSpace,
        objectives: Sequence[ObjectiveSpec],
        constraints: Sequence[ConstraintSpec],
        history: Sequence[RunResult],
        n: int = 1,
    ) -> List[ExperimentSpec]:
        raise NotImplementedError


class BaselineGridPlanner(ExperimentPlanner):
    def propose(
        self,
        *,
        domain: str,
        design_space: DesignSpace,
        objectives: Sequence[ObjectiveSpec],
        constraints: Sequence[ConstraintSpec],
        history: Sequence[RunResult],
        n: int = 1,
    ) -> List[ExperimentSpec]:
        specs: List[ExperimentSpec] = []
        history_count = len(history)
        for i in range(n):
            params = {}
            step = history_count + i + 1
            denom = max(10, step)
            for name, (lo, hi) in design_space.bounds.items():
                frac = min(1.0, step / denom)
                params[name] = lo + (hi - lo) * frac

            specs.append(
                ExperimentSpec(
                    experiment_id=f"{domain}-exp-{history_count+i+1}",
                    domain=domain,
                    parameters=params,
                    objectives=list(objectives),
                    constraints=list(constraints),
                )
            )

        return specs


class ModelBasedPlanner(ExperimentPlanner):
    """Lightweight model-based planner with BO-style acquisition.

    Surrogate: nearest-neighbor estimate over prior runs.
    Acquisition choices:
      - ucb: mean + beta * std
      - ei: expected improvement over best observed score
      - thompson: Gaussian sample(mean, std)
    """

    def __init__(
        self,
        random_candidates: int = 64,
        beta: float = 0.6,
        acquisition: AcquisitionKind = "ucb",
        seed: int = 7,
    ):
        self.random_candidates = random_candidates
        self.beta = beta
        self.acquisition = acquisition
        self.rng = random.Random(seed)

    def propose(
        self,
        *,
        domain: str,
        design_space: DesignSpace,
        objectives: Sequence[ObjectiveSpec],
        constraints: Sequence[ConstraintSpec],
        history: Sequence[RunResult],
        n: int = 1,
    ) -> List[ExperimentSpec]:
        if len(history) < 5:
            return BaselineGridPlanner().propose(
                domain=domain,
                design_space=design_space,
                objectives=objectives,
                constraints=constraints,
                history=history,
                n=n,
            )

        pool = [self._sample_point(design_space) for _ in range(self.random_candidates)]
        best_observed = self._best_observed(history, objectives)

        ranked = sorted(
            pool,
            key=lambda p: self._acquisition_value(p, history, objectives, best_observed),
            reverse=True,
        )

        out = []
        for i, params in enumerate(ranked[:n], start=1):
            out.append(
                ExperimentSpec(
                    experiment_id=f"{domain}-mb-{len(history)+i}",
                    domain=domain,
                    parameters=params,
                    objectives=list(objectives),
                    constraints=list(constraints),
                    metadata={"planner": "model_based", "acquisition": self.acquisition},
                )
            )
        return out

    def _sample_point(self, design_space: DesignSpace) -> Dict[str, float]:
        return {
            name: self.rng.uniform(lo, hi)
            for name, (lo, hi) in design_space.bounds.items()
        }

    def _acquisition_value(
        self,
        params: Dict[str, float],
        history: Sequence[RunResult],
        objectives: Sequence[ObjectiveSpec],
        best_observed: float,
    ) -> float:
        mean, std = self._surrogate_mean_std(params, history, objectives)

        if self.acquisition == "ucb":
            return mean + self.beta * std
        if self.acquisition == "ei":
            # Positive part of improvement with small exploration bonus
            return max(0.0, mean - best_observed) + 0.1 * std
        if self.acquisition == "thompson":
            return self.rng.gauss(mean, max(std, 1e-6))
        return mean

    def _surrogate_mean_std(
        self,
        params: Dict[str, float],
        history: Sequence[RunResult],
        objectives: Sequence[ObjectiveSpec],
    ) -> tuple[float, float]:
        rows = []
        for r in history:
            if r.status != "ok":
                continue
            dist = self._distance(params, r.parameters)
            score = self._score_outputs(r.outputs, objectives)
            rows.append((dist, score))

        if not rows:
            return 0.0, 1.0

        rows.sort(key=lambda t: t[0])
        k = min(7, len(rows))
        neigh = rows[:k]

        weights = [1.0 / (d + 1e-6) for d, _ in neigh]
        wsum = sum(weights)

        mean = sum((w / wsum) * s for w, (_, s) in zip(weights, neigh))
        var = sum((w / wsum) * (s - mean) ** 2 for w, (_, s) in zip(weights, neigh))

        # add spatial uncertainty term: farther neighborhood -> more uncertain
        mean_dist = sum(d for d, _ in neigh) / k
        std = math.sqrt(max(0.0, var)) + 0.2 * mean_dist
        return mean, std

    def _best_observed(self, history: Sequence[RunResult], objectives: Sequence[ObjectiveSpec]) -> float:
        vals = [self._score_outputs(r.outputs, objectives) for r in history if r.status == "ok"]
        return max(vals) if vals else 0.0

    @staticmethod
    def _score_outputs(outputs: Dict[str, float], objectives: Sequence[ObjectiveSpec]) -> float:
        total = 0.0
        for obj in objectives:
            val = float(outputs.get(obj.name, 0.0))
            total += obj.weight * (val if obj.direction == "maximize" else -val)
        return total

    @staticmethod
    def _distance(a: Dict[str, float], b: Dict[str, float]) -> float:
        keys = set(a.keys()).intersection(b.keys())
        if not keys:
            return 1.0
        return math.sqrt(sum((float(a[k]) - float(b[k])) ** 2 for k in keys))


class OptunaTPEPlanner(ExperimentPlanner):
    """Optional Optuna-backed planner.

    If Optuna isn't installed, transparently falls back to ModelBasedPlanner.
    """

    def __init__(self, seed: int = 7, startup_trials: int = 8):
        self.seed = seed
        self.startup_trials = startup_trials
        self._fallback = ModelBasedPlanner(seed=seed, acquisition="ei")

    def propose(
        self,
        *,
        domain: str,
        design_space: DesignSpace,
        objectives: Sequence[ObjectiveSpec],
        constraints: Sequence[ConstraintSpec],
        history: Sequence[RunResult],
        n: int = 1,
    ) -> List[ExperimentSpec]:
        try:
            import optuna  # type: ignore
            sampler = optuna.samplers.TPESampler(seed=self.seed, n_startup_trials=self.startup_trials)
        except Exception:
            specs = self._fallback.propose(
                domain=domain,
                design_space=design_space,
                objectives=objectives,
                constraints=constraints,
                history=history,
                n=n,
            )
            for s in specs:
                s.metadata["planner"] = "optuna_tpe_fallback"
            return specs

        specs: List[ExperimentSpec] = []
        history_count = len(history)
        for i in range(n):
            study = optuna.create_study(direction="maximize", sampler=sampler)

            # replay history into study as completed trials (approximation)
            for r in history:
                if r.status != "ok" or r.score is None:
                    continue
                trial = study.ask()
                for k, v in r.parameters.items():
                    trial.suggest_float(k, *design_space.bounds[k])
                study.tell(trial, float(r.score))

            trial = study.ask()
            params = {
                name: trial.suggest_float(name, lo, hi)
                for name, (lo, hi) in design_space.bounds.items()
            }
            specs.append(
                ExperimentSpec(
                    experiment_id=f"{domain}-optuna-{history_count+i+1}",
                    domain=domain,
                    parameters=params,
                    objectives=list(objectives),
                    constraints=list(constraints),
                    metadata={"planner": "optuna_tpe"},
                )
            )

        return specs
