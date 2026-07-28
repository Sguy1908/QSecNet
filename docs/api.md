# API guide

The interactive OpenAPI specification is available at `/docs` while the service
is running. All application endpoints are prefixed with `/api/v1`.

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/topologies` | Validate and persist a connected topology |
| `GET` | `/topologies` | List stored network designs |
| `GET` | `/topologies/{id}` | Retrieve one design |
| `POST` | `/simulations/bb84` | Execute BB84 with optional attacks |
| `POST` | `/security/analyze` | Calculate security posture and recommendations |
| `POST` | `/reports` | Store an immutable security report |
| `GET` | `/reports/{id}/export/json` | Download a report as JSON |
| `GET` | `/reports/{id}/export/csv` | Download a report as CSV |
| `POST` | `/ibm/compare` | Run an Aer calibration and optional IBM comparison |

`GET /health` and `GET /api/v1/health` provide unversioned liveness and
versioned database-readiness checks respectively.

Example BB84 request:

```json
{"rounds": 2048, "seed": 42, "attacks": [{"kind": "intercept_resend"}]}
```

`channel_noise` and `photon_loss` require a `probability` in `[0, 1]`.
`node_failure` requires `node_id`; `link_failure` requires `source` and `target`.

## IBM Quantum Runtime

The local side of `/ibm/compare` always uses Qiskit Aer. Remote execution is
opt-in: set `QSECNET_IBM_QUANTUM_TOKEN` and, when applicable,
`QSECNET_IBM_QUANTUM_INSTANCE`. Without credentials the endpoint succeeds with
`remote_available: false` and does not expose or persist credentials.
