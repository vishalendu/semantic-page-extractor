from semantic_page_extractor.normalize import normalize_text, resolve_field_label


def test_label_resolution_precedence() -> None:
    assert resolve_field_label("For Label", "Wrapped", "Aria", "Placeholder") == "For Label"
    assert resolve_field_label(None, "Wrapped", "Aria", "Placeholder") == "Wrapped"
    assert resolve_field_label(None, None, "Aria", "Placeholder") == "Aria"
    assert resolve_field_label(None, None, None, "Placeholder") == "Placeholder"


def test_normalize_text_compacts_spaces() -> None:
    assert normalize_text("  hello   world ") == "hello world"
    assert normalize_text("   ") is None
