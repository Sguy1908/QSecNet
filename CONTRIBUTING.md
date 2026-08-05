# Contributing to QSecNet

Thank you for contributing. Please use Python 3.11+, keep changes focused, add or update tests for behaviour changes, and run the checks below before opening a pull request.

```bash
pytest
ruff check backend tests
```

Use conventional, imperative commit messages such as `feat: add BB84 engine`. Do not put quantum-network business logic in the frontend; API contracts and backend tests must be established first.
