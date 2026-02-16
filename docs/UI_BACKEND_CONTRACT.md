# UI/Backend Contract (v0.1)

## Stable UI modules

1. Projects dashboard
2. Job queue + live status
3. Design space/objectives editor
4. Results explorer (metrics, trends, Pareto)
5. Recommendations panel (why next experiment)

## Backend endpoints

See `api/openapi.yaml` for endpoint contracts.

## Core objects

- Project: domain + metadata
- Job: backend (`openfoam|lammps`) + input payload + status
- Experiment: objective/constraint/design-space context
- Result: metrics + artifacts + notes

## Recommended frontend stack

- React/Next.js
- Plotly/ECharts for Pareto and trend charts
- WebSocket or polling for job status

## Recommended backend stack

- FastAPI
- Worker queue: Celery or RQ
- DB: Postgres
- Artifact store: filesystem first, S3-compatible later
