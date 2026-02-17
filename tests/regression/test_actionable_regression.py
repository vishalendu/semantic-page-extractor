from __future__ import annotations

import json
from pathlib import Path

from semantic_page_extractor import extract_actionable_elements
from semantic_page_extractor.models import PageSummary


def test_amazon_add_to_cart_dedup_regression() -> None:
    path = Path(__file__).resolve().parents[2] / "out.json"
    if not path.exists():
        return

    summary = PageSummary.model_validate(json.loads(path.read_text(encoding="utf-8")))
    actionable = extract_actionable_elements(summary)

    add_to_cart = [e for e in actionable if e.visible_text == "Add to cart"]
    assert len(add_to_cart) == 16
    assert len({e.action_signature for e in add_to_cart}) == 16
