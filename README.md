# p1 — Cognitive Simulation Engine (WIP)

This repository is evolving from hard-coded domain demos into a cognitive simulation engine.

## Target Capabilities

- Natural-language intent -> formal experiment specs
- Constraint-aware experiment planning
- Multi-objective optimization (Pareto-friendly)
- Iterative learning from experiment history
- Explainable recommendations

## What we started here

A new `mcc.cognitive` layer has been added to provide a stable architecture:

- `schema.py` — canonical dataclasses (`ExperimentSpec`, `ConstraintSpec`, `ObjectiveSpec`, `RunResult`)
- `planner.py` — planning interfaces + baseline planner
- `memory.py` — structured JSONL memory store
- `engine.py` — orchestration loop (`plan -> simulate -> store -> summarize`)

This is intentionally minimal and testable, so advanced methods (Bayesian optimization, active learning, surrogate models) can be added safely.

## Next upgrades

1. Replace baseline planner with Bayesian optimizer (BoTorch/Ax/Optuna integration)
2. Add uncertainty-aware surrogate model
3. Add active-learning acquisition policies (EI/UCB/knowledge gradient)
4. Add multi-domain simulation adapters with unit-safe constraints
5. Add cognitive explanation layer (why next experiment was selected)
