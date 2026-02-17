from __future__ import annotations

from semantic_page_extractor.models import FieldSummary, FormSummary, InteractiveElement, PageSummary
from semantic_page_extractor.output import build_output_payload


def _mk_action(sig: str, text: str, section: str = "S", role: str = "button") -> InteractiveElement:
    return InteractiveElement(
        action_signature=sig,
        role=role,
        visible_text=text,
        aria_label=None,
        disabled=False,
        section_context=section,
    )


def _summary() -> PageSummary:
    a = _mk_action("sig-a", "Add to cart", section="Phone A")
    b = _mk_action("sig-b", "Buy now", section="Phone A")
    return PageSummary(
        schema_version="1.0",
        url="https://example.com",
        title="Example",
        page_signature="page",
        headers=[],
        forms=[
            FormSummary(
                form_signature="f1",
                section_context="Phone A",
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
                submit_buttons=[a],
            )
        ],
        interactive_elements=[a, b],
    )


def test_build_output_payload_actionable_only_dedupes() -> None:
    payload = build_output_payload(_summary(), actionable_only=True)
    assert isinstance(payload, list)
    assert len(payload) == 2


def test_build_output_payload_intent_filter() -> None:
    payload = build_output_payload(_summary(), intent="add to cart", min_score=0.5, actionable_only=True)
    assert isinstance(payload, list)
    assert len(payload) == 1
    assert payload[0]["visible_text"] == "Add to cart"


def test_build_output_payload_json_format_strips_fields() -> None:
    payload = build_output_payload(_summary(), actionable_only=True, output_format="json")
    assert isinstance(payload, list)
    assert "action_signature" not in payload[0]
    assert "disabled" not in payload[0]


def test_build_output_payload_compact_format() -> None:
    payload = build_output_payload(_summary(), actionable_only=True, output_format="compact")
    assert isinstance(payload, dict)
    assert {"v", "r", "t", "c", "i"} == set(payload.keys())
