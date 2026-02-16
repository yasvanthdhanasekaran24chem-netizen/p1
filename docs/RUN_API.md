# Run API (scaffold)

## Prerequisites
- Python environment with `fastapi` and `uvicorn` installed
- For real solver runs:
  - OpenFOAM available with `bash/sh` shell for `Allrun`
  - LAMMPS executable on PATH or set `LAMMPS_CMD`

## Start server

```bash
uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload
```

## Optional API key protection

Set `P1_API_KEY` to enforce auth on all endpoints:

```bash
# PowerShell
$env:P1_API_KEY="change-me"
```

Then include header in requests:

```bash
-H "X-API-Key: change-me"
```

## Optional rate limiting

```bash
# defaults: 60 requests / 60 sec per key(or IP)
$env:P1_RATE_LIMIT_ENABLED="1"
$env:P1_RATE_LIMIT_MAX="60"
$env:P1_RATE_LIMIT_WINDOW_SEC="60"
```

## Optional audit logging

```bash
$env:P1_AUDIT_LOG_ENABLED="1"
$env:P1_AUDIT_LOG_PATH="./sim_jobs/api_audit.jsonl"
```

## Example requests

Create job:
```bash
curl -X POST http://localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{"backend":"openfoam","inputs":{"case":"pipe_flow"}}'
```

Run job (sync):
```bash
curl -X POST http://localhost:8000/jobs/<job_id>/run
```

Enqueue job:
```bash
curl -X POST "http://localhost:8000/jobs/<job_id>/enqueue?max_attempts=3"
```

Worker step (run next queued):
```bash
curl -X POST http://localhost:8000/queue/run-next
```

Worker step alias:
```bash
curl -X POST http://localhost:8000/queue/worker-step
```

Queue status:
```bash
curl http://localhost:8000/queue/<job_id>
```

Cancel queued job:
```bash
curl -X POST "http://localhost:8000/queue/<job_id>/cancel?reason=user_stop"
```

Replay dead job:
```bash
curl -X POST "http://localhost:8000/queue/<job_id>/replay?max_attempts=2"
```

Purge old finished records:
```bash
curl -X POST "http://localhost:8000/queue/purge?keep_latest=200"
```

List jobs:
```bash
curl "http://localhost:8000/jobs?limit=20"
```

Suggest experiments:
```bash
curl -X POST http://localhost:8000/experiments/suggest \
  -H "Content-Type: application/json" \
  -d '{
    "domain":"toy_process",
    "planner":"model_based",
    "design_space":{"x":[0,8],"y":[0,6]},
    "objectives":[
      {"name":"yield","direction":"maximize","weight":0.8},
      {"name":"energy","direction":"minimize","weight":0.2}
    ],
    "constraints":[{"name":"yield_floor","kind":"gte","field":"yield","value":40}],
    "n":2
  }'
```

Check backend runtime availability:
```bash
curl http://localhost:8000/health/backends
```

Get overall summary:
```bash
curl http://localhost:8000/summary
```

Liveness and readiness:
```bash
curl http://localhost:8000/health/live
curl http://localhost:8000/health/ready
```

Effective config:
```bash
curl http://localhost:8000/config/effective
```

## Run worker loop (CLI)

Run once:
```bash
python -m mcc.cognitive.worker --once --workdir ./sim_jobs
```

Run continuously:
```bash
python -m mcc.cognitive.worker --workdir ./sim_jobs --interval 2
```
