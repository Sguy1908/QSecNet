# QSecNet

<<<<<<< HEAD
QSecNet is an open-source, research-oriented platform for assessing the security posture of quantum communication networks. It combines topology modelling, BB84 simulation, modular threat injection, security analysis, and actionable recommendations.

> Status: actively being built backend-first. The frontend will be introduced only after the API contract and backend test suite are complete.

## Planned capabilities

- Design and persist quantum network topologies.
- Simulate BB84 key distribution with Qiskit Aer and optional IBM Quantum runs.
- Model intercept-resend, channel noise, photon loss, node failure, and link failure.
- Calculate QBER, fidelity, key rate, reliability, connectivity, and risk scores.
- Produce exportable security reports and a React/TypeScript visualization dashboard.

## Architecture

The FastAPI service owns all business logic. It coordinates the quantum, network, attack, analysis, recommendation, and persistence layers through typed API schemas. The future React client will consume this public API only. See [docs/architecture.md](docs/architecture.md) for details.
=======
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
>>>>>>> origin/main

## Quick start

Requires Python 3.11+.

```bash
<<<<<<< HEAD
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
uvicorn backend.main:app --reload
```

Open <http://127.0.0.1:8000/docs> for interactive OpenAPI documentation.

```bash
pytest
ruff check backend tests
```

## Repository layout

```text
backend/     FastAPI application and domain modules
tests/       Unit and integration tests
docs/        Architecture, API, and research documentation
examples/    Reproducible experiment examples
assets/      Project visual assets
```
=======
python -m venv .venv && source .venv/bin/activate
pip install -e '.[dev]'
# Optional local Aer/IBM support:
# pip install -e '.[dev,quantum,ibm]'
uvicorn backend.main:app --reload
```

OpenAPI docs: `http://localhost:8000/docs`

Run tests:
>>>>>>> origin/main

```bash
pytest
```

<<<<<<< HEAD
1. Database schema and migrations
2. Validated CRUD API
3. BB84, topology, attack, analysis, and recommendation engines
4. Full test suite and frontend dashboard
5. IBM Quantum comparisons, CI/CD, and deployment guidance

## Database migrations

```bash
alembic upgrade head
```

The Docker image runs the same migration command automatically at container startup.

## IBM Quantum hardware comparisons

Install the optional integration and set `QSECNET_IBM_QUANTUM_TOKEN` (and, if
required, `QSECNET_IBM_QUANTUM_INSTANCE`). The IBM comparison endpoint runs an
empirical prepared-state probe on the selected backend and returns its observed
hardware error rate beside the persisted simulator QBER.

```bash
pip install -e '.[ibm]'
```
=======
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
>>>>>>> origin/main

## License

Distributed under the [MIT License](LICENSE).
