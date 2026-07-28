# QSecNet

**QSecNet** is an open-source, research-oriented platform for analysing the
security posture of quantum communication networks. It models network
topologies, BB84 key distribution, adversarial conditions, and actionable
security recommendations through a typed FastAPI service and web dashboard.

## Current capabilities

- FastAPI service with OpenAPI documentation at `/docs`
- Configurable runtime settings and health endpoint
- Topology builder API with NetworkX graph validation and SQLite persistence
- Reproducible BB84 protocol simulation with intercept-resend, channel-noise,
  photon-loss, node-failure, and link-failure attack models
- Security scoring for QBER, fidelity, reliability, connectivity, weak links,
  key-rate estimates, risk levels, and prioritized remediation advice
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

For the dashboard, run `cd frontend && npm install && npm run dev`. It expects the
API at `http://localhost:8000/api/v1`; override this with `VITE_API_URL`.

## Roadmap

1. BB84 simulation and attack models
3. Security analysis, recommendations, exports, and reports
4. React dashboard and IBM Quantum Runtime comparison

## Screenshots

Dashboard screenshots will be added as the frontend is implemented.

## License

MIT. See [LICENSE](LICENSE).
