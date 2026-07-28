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

Example BB84 request:

```json
{"rounds": 2048, "seed": 42, "attacks": [{"kind": "intercept_resend"}]}
```

`channel_noise` and `photon_loss` require a `probability` in `[0, 1]`.
`node_failure` requires `node_id`; `link_failure` requires `source` and `target`.
