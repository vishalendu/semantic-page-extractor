from __future__ import annotations

from semantic_page_extractor import filter_actionable_elements, rank_actionable_elements
from semantic_page_extractor.models import InteractiveElement


def _mk(sig: str, text: str | None, section: str | None = None, role: str = "button") -> InteractiveElement:
    return InteractiveElement(
        action_signature=sig,
        role=role,
        visible_text=text,
        aria_label=None,
        disabled=False,
        section_context=section,
    )


def test_exact_match_ranks_first() -> None:
    items = [
        _mk("1", "Buy now", section="Phone A"),
        _mk("2", "Add to cart", section="Phone B"),
        _mk("3", "Compare", section="Phone C"),
    ]
    ranked = rank_actionable_elements(items, "add to cart")
    assert ranked[0].element.action_signature == "2"
    assert ranked[0].score > ranked[1].score


def test_fuzzy_match_typo_returns_expected_element() -> None:
    items = [_mk("1", "Add to cart"), _mk("2", "Proceed to checkout")]
    filtered = filter_actionable_elements(items, "ad to crt", min_score=0.35)
    assert filtered
    assert filtered[0].action_signature == "1"


def test_multi_property_match_with_section_context() -> None:
    items = [
        _mk("1", None, section="iPhone 17 Pro listing", role="image_link"),
        _mk("2", "Explore", section="Accessories", role="link"),
    ]
    filtered = filter_actionable_elements(items, "iphone 17", min_score=0.35)
    assert [e.action_signature for e in filtered] == ["1"]


def test_tie_order_is_deterministic() -> None:
    items = [_mk("b", "Add to cart"), _mk("a", "Add to cart")]
    r1 = [e.action_signature for e in filter_actionable_elements(items, "add to cart", min_score=0.1)]
    r2 = [e.action_signature for e in filter_actionable_elements(items, "add to cart", min_score=0.1)]
    assert r1 == r2 == ["a", "b"]
