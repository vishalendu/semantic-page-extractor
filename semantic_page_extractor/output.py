from __future__ import annotations

from semantic_page_extractor.actionable import (
    dedupe_actionable_elements,
    extract_actionable_elements,
    merge_actionable_elements,
)
from semantic_page_extractor.intent import filter_actionable_elements
from semantic_page_extractor.models import PageSummary


def compact_actionable_payload(payload: dict | list) -> dict | list:
    if not isinstance(payload, list):
        return payload
    if not payload:
        return {"v": 1, "r": [], "t": [], "c": [], "i": []}
    if not all(isinstance(item, dict) and "role" in item for item in payload):
        return payload

    roles = sorted({item.get("role") or "" for item in payload})
    texts = sorted({item.get("visible_text") or item.get("aria_label") or "" for item in payload})
    contexts = sorted({item.get("section_context") or "" for item in payload})
    role_idx = {value: idx for idx, value in enumerate(roles)}
    text_idx = {value: idx for idx, value in enumerate(texts)}
    context_idx = {value: idx for idx, value in enumerate(contexts)}

    items = []
    for item in payload:
        row = [
            role_idx[item.get("role") or ""],
            text_idx[item.get("visible_text") or item.get("aria_label") or ""],
            context_idx[item.get("section_context") or ""],
        ]
        if item.get("disabled"):
            row.append(1)
        items.append(row)
    return {"v": 1, "r": roles, "t": texts, "c": contexts, "i": items}


def strip_fields(payload: dict | list, blocked_keys: set[str]) -> dict | list:
    if isinstance(payload, dict):
        return {k: strip_fields(v, blocked_keys) for k, v in payload.items() if k not in blocked_keys}
    if isinstance(payload, list):
        return [strip_fields(item, blocked_keys) for item in payload]
    return payload


def build_output_payload(
    summary: PageSummary,
    *,
    actionable_only: bool = False,
    intent: str | None = None,
    min_score: float = 0.45,
    max_results: int | None = None,
    output_format: str | None = None,
) -> dict | list:
    if intent:
        elements = filter_actionable_elements(
            merge_actionable_elements(summary),
            query=intent,
            min_score=min_score,
            max_results=max_results,
        )
        if actionable_only:
            elements = dedupe_actionable_elements(elements)
        payload: dict | list = [item.model_dump(mode="json") for item in elements]
    elif actionable_only:
        payload = [item.model_dump(mode="json") for item in extract_actionable_elements(summary)]
    else:
        payload = summary.model_dump(mode="json")

    if output_format == "compact":
        return compact_actionable_payload(payload)
    if output_format == "json":
        return strip_fields(payload, {"action_signature", "disabled"})
    return payload
