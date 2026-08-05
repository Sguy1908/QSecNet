"""Security-report export formatters with no runtime browser dependency."""

from __future__ import annotations

import csv
import io
from typing import Any


def report_document(report: Any, recommendations: list[Any]) -> dict[str, Any]:
    """Create a stable JSON document from ORM report and recommendation records."""
    return {
        "report": {
            "id": report.id,
            "simulation_id": report.simulation_id,
            "security_score": report.security_score,
            "risk_level": report.risk_level.value,
            "metrics": report.metrics,
            "created_at": report.created_at.isoformat(),
        },
        "recommendations": [
            {
                "title": recommendation.title,
                "description": recommendation.description,
                "priority": recommendation.priority.value,
                "category": recommendation.category,
            }
            for recommendation in recommendations
        ],
    }


def report_csv(document: dict[str, Any]) -> str:
    """Render one CSV row per metric for spreadsheet tooling."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["report_id", "risk_level", "metric", "value"])
    report = document["report"]
    for name, value in report["metrics"].items():
        writer.writerow([report["id"], report["risk_level"], name, value])
    return output.getvalue()


def _pdf_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def report_pdf(document: dict[str, Any]) -> bytes:
    """Render a compact standards-compliant PDF without an external renderer.

    The document deliberately uses built-in Helvetica and plain text so reports
    stay reproducible in a container and can be opened by any PDF reader.
    """
    report = document["report"]
    lines = [
        "QSecNet Security Report",
        f"Report ID: {report['id']}",
        f"Risk level: {report['risk_level']}",
        f"Security score: {report['security_score']}",
        "Metrics:",
    ]
    lines.extend(f"- {name}: {value}" for name, value in report["metrics"].items())
    lines.append("Recommendations:")
    lines.extend(
        f"- [{item['priority']}] {item['title']}: {item['description']}"
        for item in document["recommendations"]
    )
    text_commands = ["BT", "/F1 10 Tf", "50 780 Td", "14 TL"]
    for index, line in enumerate(lines):
        if index:
            text_commands.append("T*")
        text_commands.append(f"({_pdf_escape(line)}) Tj")
    text_commands.append("ET")
    stream = "\n".join(text_commands).encode("latin-1", "replace")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>"
        ),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{index} 0 obj\n".encode())
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")
    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode())
    pdf.extend(b"".join(f"{offset:010d} 00000 n \n".encode() for offset in offsets[1:]))
    pdf.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n"
        ).encode()
    )
    return bytes(pdf)
