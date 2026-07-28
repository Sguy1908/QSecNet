# QSecNet

**QSecNet** is an open-source, research-oriented platform for analysing quantum
network security. The frontend consumes a FastAPI backend exposed at
`http://localhost:8000/api/v1`.

## Backend capabilities

- `GET /api/v1/health` readiness + runtime configuration summary
- Topology CRUD + graph validation (`/api/v1/topologies`)
- BB84 simulation with composable attacks (`/api/v1/simulations/bb84`)
- Persisted simulations, attacks, analyses, recommendations, and reports
- Security analysis metrics and ranked recommendations
- Report generation and export (`json` / `csv`)
- Optional IBM Quantum adapter (`/api/v1/ibm/compare`) with safe disabled mode

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e '.[dev]'
# Optional local Aer/IBM support:
# pip install -e '.[dev,quantum,ibm]'
uvicorn backend.main:app --reload
```

OpenAPI docs: `http://localhost:8000/docs`

Run tests:

```bash
pytest
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## Environment variables

- `QSECNET_API_PREFIX` (default `/api/v1`)
- `QSECNET_DATABASE_URL` (default `sqlite:///./qsecnet.db`)
- `QSECNET_CORS_ORIGINS` (default `http://localhost:5173`)
- `QSECNET_ENABLE_IBM` (`true`/`false`, default `false`)
- `QSECNET_IBM_TOKEN` (required only when IBM integration is enabled)

When IBM is disabled or credentials are missing, IBM endpoints return a clean
unavailable response instead of failing.

## License

MIT. See [LICENSE](LICENSE).
