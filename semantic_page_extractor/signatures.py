from __future__ import annotations

import hashlib
import json

from semantic_page_extractor.normalize import normalize_text


def sha256_canonical(payload: dict | list) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def field_signature(label: str | None, input_type: str, section_context: str | None) -> str:
    return sha256_canonical(
        {
            "label": normalize_text(label),
            "type": normalize_text(input_type) or "text",
            "section_context": normalize_text(section_context),
        }
    )


def action_signature(visible_text: str | None, role: str, section_context: str | None) -> str:
    return sha256_canonical(
        {
            "visible_text": normalize_text(visible_text),
            "role": normalize_text(role) or "",
            "section_context": normalize_text(section_context),
        }
    )


def form_signature(field_signatures: list[str], submit_signatures: list[str], section_context: str | None) -> str:
    return sha256_canonical(
        {
            "section_context": normalize_text(section_context),
            "field_signatures": sorted(field_signatures),
            "submit_signatures": sorted(submit_signatures),
        }
    )


def page_signature(title: str, headers: list[str], forms_count: int, interactive_count: int) -> str:
    return sha256_canonical(
        {
            "title": normalize_text(title),
            "headers": sorted((normalize_text(h) or "") for h in headers),
            "forms_count": forms_count,
            "interactive_count": interactive_count,
        }
    )
