# QSecNet

**QSecNet** is an open-source, research-oriented platform for analysing the
security posture of quantum communication networks. It models network
topologies, BB84 key distribution, adversarial conditions, and actionable
security recommendations through a typed FastAPI service and web dashboard.

## Current capabilities

- FastAPI service with OpenAPI documentation at `/docs`
- Configurable runtime settings and health endpoint
- Foundation for topology, simulation, attacks, analysis, reports, and IBM
  Quantum Runtime comparison
- Automated linting and tests in GitHub Actions

## Architecture

```text
React dashboard -> FastAPI API -> domain services -> SQLite / Qiskit / IBM Runtime
```

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e '.[dev,quantum]'
uvicorn backend.main:app --reload
```

Open `http://localhost:8000/docs` and run `pytest` to verify the installation.

## Roadmap

1. Network topology persistence and builder APIs
2. BB84 simulation and attack models
3. Security analysis, recommendations, exports, and reports
4. React dashboard and IBM Quantum Runtime comparison

## Screenshots

Dashboard screenshots will be added as the frontend is implemented.

## License

MIT. See [LICENSE](LICENSE).
