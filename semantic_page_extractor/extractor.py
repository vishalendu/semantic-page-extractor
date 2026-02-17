from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import ValidationError

from semantic_page_extractor.browser_script import EXTRACTION_SCRIPT
from semantic_page_extractor.errors import ExtractionError
from semantic_page_extractor.models import FieldSummary, FormSummary, InteractiveElement, PageSummary
from semantic_page_extractor.normalize import normalize_text, resolve_field_label, sort_key
from semantic_page_extractor.output import build_output_payload
from semantic_page_extractor.signatures import (
    action_signature,
    field_signature,
    form_signature,
    page_signature,
)

if TYPE_CHECKING:
    from playwright.async_api import Page

SCHEMA_VERSION = "1.0"


def _to_interactive(raw: dict) -> InteractiveElement:
    text = normalize_text(raw.get("visible_text"))
    role = normalize_text(raw.get("role")) or "button"
    section_context = normalize_text(raw.get("section_context"))
    return InteractiveElement(
        action_signature=action_signature(text, role, section_context),
        role=role,
        visible_text=text,
        aria_label=normalize_text(raw.get("aria_label")),
        disabled=bool(raw.get("disabled", False)),
        section_context=section_context,
    )


def _to_field(raw: dict) -> FieldSummary:
    label = resolve_field_label(
        raw.get("label_for"),
        raw.get("label_wrapped"),
        raw.get("aria_label"),
        raw.get("placeholder"),
    )
    field_type = normalize_text(raw.get("type")) or "text"
    section_context = normalize_text(raw.get("section_context"))
    options = raw.get("options")
    normalized_options = (
        sorted(filter(None, (normalize_text(v) for v in options))) if isinstance(options, list) else None
    )
    return FieldSummary(
        field_signature=field_signature(label, field_type, section_context),
        label=label,
        type=field_type,
        required=bool(raw.get("required", False)),
        placeholder=normalize_text(raw.get("placeholder")),
        options=normalized_options or None,
        disabled=bool(raw.get("disabled", False)),
    )


def _to_form(raw: dict) -> FormSummary:
    fields = [_to_field(item) for item in raw.get("fields", [])]
    submits = [_to_interactive(item) for item in raw.get("submit_buttons", [])]
    fields.sort(key=lambda f: sort_key(f.field_signature, f.label, f.type))
    submits.sort(key=lambda a: sort_key(a.action_signature, a.role, a.visible_text))
    section_context = normalize_text(raw.get("section_context"))
    return FormSummary(
        form_signature=form_signature(
            [f.field_signature for f in fields],
            [s.action_signature for s in submits],
            section_context,
        ),
        section_context=section_context,
        fields=fields,
        submit_buttons=submits,
    )


async def extract_page_semantics(page: "Page") -> PageSummary:
    try:
        raw = await page.evaluate(EXTRACTION_SCRIPT)
    except Exception as exc:  # pragma: no cover
        raise ExtractionError(f"Browser extraction failed: {exc}") from exc

    try:
        headers = sorted(
            filter(None, (normalize_text(h) for h in raw.get("headers", []))),
            key=lambda h: h.lower(),
        )
        forms = [_to_form(item) for item in raw.get("forms", [])]
        interactive = [_to_interactive(item) for item in raw.get("interactive_elements", [])]

        forms.sort(key=lambda f: sort_key(f.form_signature, f.section_context))
        interactive.sort(key=lambda a: sort_key(a.action_signature, a.role, a.visible_text))

        return PageSummary(
            schema_version=SCHEMA_VERSION,
            url=str(raw.get("url") or ""),
            title=normalize_text(raw.get("title")) or "",
            page_signature=page_signature(
                title=raw.get("title") or "",
                headers=headers,
                forms_count=len(forms),
                interactive_count=len(interactive),
            ),
            headers=headers,
            forms=forms,
            interactive_elements=interactive,
        )
    except ValidationError as exc:
        raise ExtractionError(f"Schema validation failed: {exc}", code="SCHEMA_VALIDATION_FAILED") from exc
    except Exception as exc:
        raise ExtractionError(f"Semantic extraction failed: {exc}") from exc


async def extract_from_url(
    url: str,
    wait_until: str = "load",
    *,
    actionable_only: bool = False,
    intent: str | None = None,
    min_score: float = 0.45,
    max_results: int | None = None,
    output_format: str | None = None,
) -> PageSummary | dict | list:
    try:
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url, wait_until=wait_until)
            result: PageSummary | dict | list = await extract_page_semantics(page)
            if actionable_only or intent or max_results is not None or output_format:
                result = build_output_payload(
                    result,
                    actionable_only=actionable_only,
                    intent=intent,
                    min_score=min_score,
                    max_results=max_results,
                    output_format=output_format,
                )
            await browser.close()
            return result
    except Exception as exc:
        raise ExtractionError(f"URL extraction failed: {exc}", code="URL_EXTRACTION_FAILED") from exc
