# Current Capabilities Snapshot

## Cognitive engine
- Experiment schema + run result memory (JSONL)
- Baseline planner
- Model-based planner with acquisition modes: UCB, EI, Thompson
- Optional Optuna-TPE planner entrypoint (fallback if dependency missing)
- Constraint handling (discard/soft-penalty)
- Pareto front extraction
- Explainability notes per run (`planner=...`, `acquisition=...`)

## Domain support
- Bridge to existing `mcc.core` domain adapters
- Working cognitive reaction demo (stoichiometry)
- Toy objective demo (yield/energy)

## Simulation platform foundations
- Unified adapter contract (`SimulationAdapter`)
- OpenFOAM adapter (runtime path + parse contract, WSL-aware)
- LAMMPS adapter (runtime path + parse contract, WSL-aware)
- SU2 adapter skeleton
- Code_Saturne adapter skeleton
- Quantum ESPRESSO adapter skeleton
- API contract draft (`api/openapi.yaml`)
- FastAPI server scaffold (`api/server.py`)
- Service layer for jobs + experiment suggestions (`mcc/cognitive/service.py`)
- SQLite-backed job/result persistence (`mcc/cognitive/job_store.py`)
- Queue lifecycle support (`queued -> running -> completed/failed/dead`)
- Retry policy with max attempts and dead-lettering
- Queue operations: cancel, dead-letter replay, retention purge
- Worker CLI loop (`python -m mcc.cognitive.worker`) for continuous processing
- Backend health check endpoint (`/health/backends`)
- Summary endpoint (`/summary`), queue endpoints, and job listing endpoint (`/jobs`)
- Optional API key auth guard (`P1_API_KEY` + `X-API-Key`)
- Optional in-memory API rate limiting
- Optional API audit log (JSONL)
- Health probes (`/health/live`, `/health/ready`) and effective-config endpoint
- Structured API error payloads with error codes
- UI/backend integration guide (`docs/UI_BACKEND_CONTRACT.md`)

## Known gaps
- Robust production parser pipeline from native solver outputs to `metrics.json`
- Full Optuna dependency integration
- Stable frontend implementation
- SU2 and Code_Saturne are scaffolded but not installed on host yet
