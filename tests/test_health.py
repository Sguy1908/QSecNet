from backend.main import create_app


def test_application_exposes_health_operation() -> None:
    app = create_app()
    routes = {route.path for route in app.routes}

    assert "/health" in routes
