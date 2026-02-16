# Cognitive Engine Build Plan (Practical)

## Goal
Build a Jarvis-like cognitive experimentation engine for engineering simulation:
- understand objectives/constraints,
- propose next experiments intelligently,
- run simulations,
- learn from history,
- explain decisions.

## What we need (core building blocks)

1. **Canonical Experiment Schema**
   - params, objectives, constraints, metadata, run result
2. **Planner Interface**
   - baseline planner + model-based planner + future Bayesian planner
3. **Simulation Adapter Layer**
   - plug multiple domains (reaction, mass-balance, energy, etc.)
4. **Memory Layer**
   - append-only experimental history + retrieval
5. **Constraint Engine**
   - hard feasibility checks before optimization reward
6. **Objective Engine**
   - weighted scalar score + Pareto support
7. **Explanation Layer**
   - why candidate chosen, what uncertainty drove exploration

## Advanced concepts to integrate

- **Bayesian Optimization** (BoTorch/Ax style for expensive black-box problems)
- **Acquisition functions**: UCB, EI, Thompson sampling
- **Surrogate modeling**: GP/TPE/NN-based approximations
- **Active learning loop**: exploit best regions + explore uncertain regions
- **Multi-objective optimization**: Pareto front maintenance and selection

## Current status in repo

Implemented now:
- `mcc.cognitive.schema`
- `mcc.cognitive.memory`
- `mcc.cognitive.engine`
- `mcc.cognitive.planner` with:
  - `BaselineGridPlanner`
  - `ModelBasedPlanner` with acquisition modes (`ucb`, `ei`, `thompson`)

## Phase roadmap

### Phase 1 (done)
- stable cognitive loop and persisted history

### Phase 2 (in progress)
- model-based acquisition planner with uncertainty-aware proposals

### Phase 3 (implemented)
- Pareto utilities + constrained multi-objective selection support
- domain adapter bridge (`DomainSimulationBridge`) for cognitive layer
- penalty modes in engine (`discard` / `soft`) for infeasible trials

### Phase 4 (started)
- optional Optuna planner entrypoint (`OptunaTPEPlanner`) with graceful fallback
- real Bayesian posterior + formal EI/UCB/NEI (pending full dependency integration)
- explainability notes in run results (planner + acquisition)

### Phase 5
- natural-language intent -> ExperimentSpec compiler
- explainability + recommendation narrative

## Tooling notes

- Browser research is enabled and usable.
- `web_search` currently requires API setup; until then use `web_fetch` + browser.
