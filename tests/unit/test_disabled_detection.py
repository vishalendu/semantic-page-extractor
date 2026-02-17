from semantic_page_extractor.extractor import _to_field, _to_interactive


def test_field_disabled_detection() -> None:
    field = _to_field(
        {
            "type": "text",
            "label_for": "Name",
            "required": False,
            "placeholder": None,
            "disabled": True,
            "section_context": "Profile",
        }
    )
    assert field.disabled is True


def test_interactive_disabled_detection() -> None:
    action = _to_interactive(
        {
            "role": "button",
            "visible_text": "Save",
            "aria_label": None,
            "disabled": True,
            "section_context": "Profile",
        }
    )
    assert action.disabled is True
