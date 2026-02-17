from __future__ import annotations

import json
from pathlib import Path

from semantic_page_extractor import filter_actionable_from_summary
from semantic_page_extractor.models import PageSummary


def test_amazon_intent_filter_add_to_cart_regression() -> None:
    path = Path(__file__).resolve().parents[2] / "out.json"
    if not path.exists():
        return

    summary = PageSummary.model_validate(json.loads(path.read_text(encoding="utf-8")))
    filtered = filter_actionable_from_summary(summary, "add to cart", min_score=0.55)

    assert len(filtered) == 16
    assert all(e.visible_text == "Add to cart" for e in filtered)
    assert len({e.action_signature for e in filtered}) == 16
