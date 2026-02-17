from __future__ import annotations

from semantic_page_extractor.models import InteractiveElement, PageSummary
from semantic_page_extractor.normalize import sort_key


def _actionable_key(
    element: InteractiveElement,
) -> tuple[str, str, str | None, str | None, str | None]:
    return (
        element.action_signature,
        element.role,
        element.visible_text,
        element.aria_label,
        element.section_context,
    )


def merge_actionable_elements(summary: PageSummary) -> list[InteractiveElement]:
    merged: list[InteractiveElement] = [*summary.interactive_elements]
    for form in summary.forms:
        merged.extend(form.submit_buttons)
    merged.sort(key=lambda e: sort_key(*_actionable_key(e)))
    return merged


def dedupe_actionable_elements(elements: list[InteractiveElement]) -> list[InteractiveElement]:
    ordered = sorted(elements, key=lambda e: sort_key(*_actionable_key(e)))
    deduped: list[InteractiveElement] = []
    seen: set[tuple[str, str, str | None, str | None, str | None]] = set()
    for element in ordered:
        key = _actionable_key(element)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(element)
    return deduped


def extract_actionable_elements(summary: PageSummary) -> list[InteractiveElement]:
    return dedupe_actionable_elements(merge_actionable_elements(summary))
