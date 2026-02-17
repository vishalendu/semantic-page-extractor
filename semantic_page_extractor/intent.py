from __future__ import annotations

import re
from dataclasses import dataclass
from difflib import SequenceMatcher

from semantic_page_extractor.models import InteractiveElement, PageSummary
from semantic_page_extractor.normalize import normalize_text, sort_key

from .actionable import extract_actionable_elements

_TOKEN_RE = re.compile(r"[a-z0-9]+")


@dataclass(frozen=True)
class RankedActionableElement:
    element: InteractiveElement
    score: float


def _tokens(value: str | None) -> list[str]:
    if not value:
        return []
    return _TOKEN_RE.findall(value.lower())


def _search_fields(element: InteractiveElement) -> list[str]:
    return [
        normalize_text(element.visible_text) or "",
        normalize_text(element.aria_label) or "",
        normalize_text(element.section_context) or "",
        normalize_text(element.role) or "",
    ]


def _search_text(element: InteractiveElement) -> str:
    return " ".join(part for part in _search_fields(element) if part).strip().lower()


def _score_element(element: InteractiveElement, query: str) -> float:
    q = (normalize_text(query) or "").lower()
    if not q:
        return 0.0

    fields = _search_fields(element)
    haystack = _search_text(element)
    q_tokens = _tokens(q)
    if not haystack:
        return 0.0

    exact = 1.0 if any(q in field.lower() for field in fields if field) else 0.0
    token_hits = sum(1 for token in q_tokens if token in haystack) if q_tokens else 0
    token_coverage = (token_hits / len(q_tokens)) if q_tokens else 0.0
    fuzzy = max(SequenceMatcher(None, q, field.lower()).ratio() for field in fields + [haystack] if field)
    return round((0.5 * exact) + (0.3 * token_coverage) + (0.2 * fuzzy), 6)


def rank_actionable_elements(
    elements: list[InteractiveElement],
    query: str,
) -> list[RankedActionableElement]:
    ranked = [
        RankedActionableElement(element=element, score=_score_element(element, query))
        for element in elements
    ]
    ranked.sort(
        key=lambda item: (
            -item.score,
            *sort_key(
                item.element.action_signature,
                item.element.role,
                item.element.visible_text,
                item.element.aria_label,
                item.element.section_context,
            ),
        )
    )
    return ranked


def filter_actionable_elements(
    elements: list[InteractiveElement],
    query: str,
    min_score: float = 0.45,
    max_results: int | None = None,
) -> list[InteractiveElement]:
    ranked = rank_actionable_elements(elements, query)
    filtered = [item.element for item in ranked if item.score >= min_score]
    return filtered[:max_results] if max_results is not None else filtered


def filter_actionable_from_summary(
    summary: PageSummary,
    query: str,
    min_score: float = 0.45,
    max_results: int | None = None,
) -> list[InteractiveElement]:
    actionable = extract_actionable_elements(summary)
    return filter_actionable_elements(
        actionable,
        query=query,
        min_score=min_score,
        max_results=max_results,
    )
