from backend.main import RequestLoggingMiddleware, create_app


def test_openapi_contract_exposes_all_backend_feature_routes() -> None:
    paths = create_app().openapi()["paths"]

    assert "/api/v1/projects" in paths
    assert "/api/v1/projects/{project_id}/simulations" in paths
    assert "/api/v1/simulations/{simulation_id}/attacks" in paths
    assert "/api/v1/simulations/{simulation_id}/security-reports" in paths
    assert "/api/v1/security-reports/{report_id}/export/pdf" in paths
    assert "/api/v1/simulations/{simulation_id}/ibm-comparison" in paths


def test_application_installs_request_correlation_middleware() -> None:
    app = create_app()

    assert any(middleware.cls is RequestLoggingMiddleware for middleware in app.user_middleware)
