# QSecNet

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

## Quick start

Requires Python 3.11+.

```bash
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

## Roadmap

1. Database schema and migrations
2. Validated CRUD API
3. BB84, topology, attack, analysis, and recommendation engines
4. Full test suite and frontend dashboard
5. IBM Quantum comparisons, CI/CD, and deployment guidance

## Database migrations

```bash
alembic upgrade head
```

## IBM Quantum hardware comparisons

Install the optional integration and set `QSECNET_IBM_QUANTUM_TOKEN` (and, if
required, `QSECNET_IBM_QUANTUM_INSTANCE`). The IBM comparison endpoint runs an
empirical prepared-state probe on the selected backend and returns its observed
hardware error rate beside the persisted simulator QBER.

```bash
pip install -e '.[ibm]'
```

## License

Distributed under the [MIT License](LICENSE).
