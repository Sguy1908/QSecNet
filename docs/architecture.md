# QSecNet architecture

QSecNet follows a layered, backend-first architecture.

```mermaid
flowchart LR
    Client[Future React client] --> API[FastAPI / typed schemas]
    API --> Services[Application services]
    Services --> Network[NetworkX topology engine]
    Services --> Quantum[Qiskit BB84 engine]
    Services --> Attacks[Modular attack engine]
    Services --> Analysis[Security analysis and recommendations]
    Services --> DB[(SQLite / SQLAlchemy)]
    Quantum -. optional .-> IBM[IBM Quantum Runtime]
```

## Boundaries

- `api`: HTTP routing, validation, status codes, and API schemas.
- `models` and `database`: persistence entities and database sessions.
- `simulator`, `attacks`, `analyzer`, `recommendation_engine`: pure domain logic.
- `utils`: shared cross-cutting concerns only.

Dependencies point inward: HTTP and persistence adapt the domain; domain modules do not import FastAPI or database sessions.

## Persistence

SQLite is the development default. Alembic owns versioned schema changes in `migrations/`; the initial schema models projects, versioned topologies, nodes, quantum links, simulations, attacks, security reports, and recommendations.
