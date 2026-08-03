import json
import logging

from backend.utils.observability import JsonFormatter


def test_json_formatter_includes_correlation_id() -> None:
    record = logging.LogRecord("qsecnet", logging.INFO, "", 0, "completed", (), None)
    record.request_id = "request-123"  # type: ignore[attr-defined]

    payload = json.loads(JsonFormatter().format(record))

    assert payload["request_id"] == "request-123"
    assert payload["message"] == "completed"
