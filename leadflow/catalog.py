from __future__ import annotations

import re

SERVICES = [
    {
        "id": "crm-automation",
        "name": "CRM and workflow automation",
        "summary": "Lead capture, assignment, follow-up workflows, and conversion dashboards.",
        "keywords": ["crm", "lead", "enquiry", "whatsapp", "follow-up", "dashboard", "automation"],
    },
    {
        "id": "web-platform",
        "name": "Custom web platform",
        "summary": "Responsive frontend, authenticated backend APIs, and admin operations.",
        "keywords": ["website", "web", "portal", "frontend", "backend", "api", "admin"],
    },
    {
        "id": "data-digitization",
        "name": "Document and data digitization",
        "summary": "Human-reviewed extraction and structured import of forms or documents.",
        "keywords": ["ocr", "pdf", "document", "extraction", "digitization", "import"],
    },
]

CASE_STUDIES = {
    "crm-automation": {
        "title": "Education enquiry workflow",
        "evidence": "Built lead and enquiry management plus Gemini-assisted conversion insights for an education administration platform.",
    },
    "web-platform": {
        "title": "Multi-tenant education platform",
        "evidence": "Built Django APIs and a Next.js frontend for institute administration and role-based workflows.",
    },
    "data-digitization": {
        "title": "Assessment content collector",
        "evidence": "Built a Django review pipeline for structured question data, checksum validation, and editable AI-assisted conversions.",
    },
}


def search_services(query: str) -> list[dict[str, str]]:
    if not isinstance(query, str) or not query.strip() or len(query) > 300:
        raise ValueError("query must be 1–300 characters")
    words = set(re.findall(r"[a-z0-9]+", query.lower()))
    ranked = []
    for service in SERVICES:
        hits = sum(bool(words & set(re.findall(r"[a-z0-9]+", keyword))) for keyword in service["keywords"])
        if hits:
            ranked.append((hits, service))
    ranked.sort(key=lambda item: (-item[0], item[1]["id"]))
    return [{k: value for k, value in service.items() if k != "keywords"} for _, service in ranked]


def get_case_study(service_id: str) -> dict[str, str]:
    if service_id not in CASE_STUDIES:
        raise ValueError("unknown service_id")
    return {"service_id": service_id, **CASE_STUDIES[service_id]}
