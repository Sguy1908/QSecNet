# API documentation

The API is served with OpenAPI documentation at `/docs` and a machine-readable schema at `/openapi.json`. Domain endpoints will be added incrementally with their request/response schemas and error semantics.

## Operations

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Service readiness and runtime environment |
| `POST` / `GET` | `/api/v1/projects` | Create or list analysis projects |
| `GET` / `PATCH` / `DELETE` | `/api/v1/projects/{project_id}` | Retrieve, change, or remove a project |
| `POST` / `GET` | `/api/v1/projects/{project_id}/topologies` | Create or list project topologies |
| `POST` / `GET` | `/api/v1/topologies/{topology_id}/nodes` | Create or list network nodes |
| `POST` | `/api/v1/topologies/{topology_id}/links` | Create a validated quantum link |
| `POST` | `/api/v1/projects/{project_id}/simulations` | Execute and persist a BB84 run |
| `GET` | `/api/v1/simulations/{simulation_id}` | Retrieve BB84 inputs, status, and metrics |
| `GET` | `/api/v1/topologies/{topology_id}/network-analysis` | Calculate topology reliability and connectivity |
| `POST` | `/api/v1/topologies/{topology_id}/routes` | Find an operational minimum-risk route |
| `POST` / `GET` | `/api/v1/simulations/{simulation_id}/attacks` | Execute or retrieve modular threat results |
| `POST` | `/api/v1/simulations/{simulation_id}/security-reports` | Calculate and persist a security assessment |
| `GET` | `/api/v1/security-reports/{report_id}` | Retrieve report metrics and risk level |
| `POST` / `GET` | `/api/v1/security-reports/{report_id}/recommendations` | Generate or retrieve mitigations |
| `GET` | `/api/v1/security-reports/{report_id}/export/{json,csv,pdf}` | Download an assessment export |
| `POST` | `/api/v1/simulations/{simulation_id}/ibm-comparison` | Compare simulator QBER with IBM hardware |
