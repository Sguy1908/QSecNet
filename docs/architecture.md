# Architecture

QSecNet uses a layered architecture so protocol, attack, analysis, and HTTP
concerns remain independently testable.

```mermaid
flowchart LR
  UI[React / Vite dashboard] --> API[FastAPI typed REST API]
  API --> T[Topology service]
  API --> S[BB84 simulation]
  S --> A[Attack plug-ins]
  API --> M[Security analyzer]
  M --> R[Recommendation engine]
  T --> DB[(SQLite / SQLAlchemy)]
  S -. optional .-> Q[Qiskit Aer / IBM Runtime]
```

## Package responsibilities

| Package | Responsibility |
| --- | --- |
| `backend/api` | Validation, OpenAPI schemas, and REST endpoints |
| `backend/simulator` | BB84 protocol execution and transcript generation |
| `backend/attacks` | Extensible channel and adversary perturbations |
| `backend/analyzer` | QBER, graph, reliability, and score calculations |
| `backend/recommendation_engine` | Metric-driven remediation guidance |
| `backend/database` / `models` | SQLAlchemy persistence lifecycle and entities |

## BB84 analysis sequence

```mermaid
sequenceDiagram
  participant U as Researcher
  participant A as API
  participant B as BB84 simulator
  participant X as Attack engine
  participant S as Security analyzer
  U->>A: POST /simulations/bb84
  A->>B: prepare, measure, sift bases
  B->>X: transcript + attack configuration
  X-->>A: altered observations and delivery rate
  U->>A: POST /security/analyze
  A->>S: topology + observed result
  S-->>A: metrics, score, risk, recommendations
```

The core BB84 implementation is protocol-level and deterministic for a supplied
seed. Qiskit Aer and IBM Runtime remain optional extras because hardware access
requires user-managed credentials and queue availability.
