from __future__ import annotations

from semantic_page_extractor import extract_actionable_elements
from semantic_page_extractor.models import FieldSummary, FormSummary, InteractiveElement, PageSummary


def _mk_action(sig: str, text: str, role: str = "button", section: str | None = None) -> InteractiveElement:
    return InteractiveElement(
        action_signature=sig,
        role=role,
        visible_text=text,
        aria_label=None,
        disabled=False,
        section_context=section,
    )


def test_extract_actionable_elements_deduplicates_between_forms_and_global() -> None:
    shared = _mk_action("sig-1", "Add to cart", role="button", section="Product A")
    only_global = _mk_action("sig-2", "Buy now", role="button", section="Product A")

    summary = PageSummary(
        schema_version="1.0",
        url="https://example.com",
        title="Example",
        page_signature="page",
        headers=[],
        forms=[
            FormSummary(
                form_signature="form-1",
                section_context="Product A",
                fields=[
                    FieldSummary(
                        field_signature="field-1",
                        label="Qty",
                        type="number",
                        required=False,
                        placeholder=None,
                        options=None,
                        disabled=False,
                    )
                ],
                submit_buttons=[shared],
            )
        ],
        interactive_elements=[shared, only_global],
    )

    result = extract_actionable_elements(summary)
    assert len(result) == 2
    assert {(e.action_signature, e.visible_text) for e in result} == {
        ("sig-1", "Add to cart"),
        ("sig-2", "Buy now"),
    }


def test_extract_actionable_elements_is_deterministic() -> None:
    a = _mk_action("b", "B")
    b = _mk_action("a", "A")
    summary = PageSummary(
        schema_version="1.0",
        url="https://example.com",
        title="Example",
        page_signature="page",
        headers=[],
        forms=[FormSummary(form_signature="f", section_context=None, fields=[], submit_buttons=[a])],
        interactive_elements=[b, a],
    )
    r1 = extract_actionable_elements(summary)
    r2 = extract_actionable_elements(summary)
    assert [e.action_signature for e in r1] == [e.action_signature for e in r2]
