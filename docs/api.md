# API documentation

<<<<<<< HEAD
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
=======
All backend endpoints are served under `/api/v1`.

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Service health, environment, and readiness |
| `POST` | `/topologies/validate` | Validate topology graph payload |
| `POST` | `/topologies` | Persist topology |
| `GET` | `/topologies` | List topologies |
| `GET` | `/topologies/{id}` | Get topology |
| `PUT` | `/topologies/{id}` | Update topology |
| `DELETE` | `/topologies/{id}` | Delete topology |
| `POST` | `/simulations/bb84` | Run + persist BB84 simulation |
| `GET` | `/simulations` | List simulations |
| `GET` | `/simulations/{id}` | Get persisted simulation |
| `GET` | `/simulations/{id}/attacks` | Get persisted attack summary |
| `POST` | `/security/analyze` | Compute security metrics + recommendations |
| `POST` | `/recommendations/generate` | Generate ranked recommendations |
| `POST` | `/reports` | Create persisted report |
| `GET` | `/reports/{id}` | Get report |
| `GET` | `/reports/{id}/export?format=json|csv` | Export report |
| `POST` | `/ibm/compare` | Aer/internal vs IBM adapter status/metadata |

## Frontend compatibility notes

`POST /simulations/bb84` keeps the existing frontend fields:

- `shared_key`
- `key_length`
- `qber`
- `success_probability`
- `sifted_bits`
- `delivery_probability`
- `attacks`
- `affected_nodes`
- `affected_links`

Additional fields are also returned (`id`, `provider`, `raw_key_bits`,
`sifted_key`, `estimated_secure_key_rate`, `metadata`) for richer analysis.

## Attack payloads

`kind` supports:

- `intercept_resend`
- `channel_noise` (`probability` required)
- `photon_loss` (`probability` required)
- `node_failure` (`node_id` required)
- `link_failure` (`source` + `target` required)

## Topology link parameters

Each topology link supports:

- `fidelity`
- `loss_probability`
- `decoherence_time` (or compatibility alias `decoherence_time_us`)
- `noise_level`
>>>>>>> origin/main
