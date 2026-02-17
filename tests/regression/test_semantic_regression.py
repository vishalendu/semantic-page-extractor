from __future__ import annotations

from pathlib import Path

import pytest

from semantic_page_extractor import extract_page_semantics

pytest.importorskip("playwright.async_api")

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures"


def _load_fixture(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def _coverage_fixture() -> str:
    return """
    <html><head><title>Semantic Coverage</title></head><body>
      <h1>Checkout</h1>
      <form>
        <label for='email'>Email</label><input id='email' type='email' required>
        <label for='country'>Country</label>
        <select id='country'><option>US</option><option>IN</option></select>
        <label><input type='checkbox' aria-label='Accept Terms'> Accept Terms</label>
        <input type='submit' value='Pay Now'>
      </form>
      <a href='/catalog?categoryId=BIRDS'><img src='/images/sm_birds.gif' alt='Bird Category'></a>
      <a href='/help'>Help</a>
      <map name='m1'>
        <area href='/catalog?categoryId=DOGS' alt='Dogs' shape='rect'/>
      </map>
      <img src='/images/splash.gif' usemap='#m1'/>
      <button aria-label='Open Help'></button>
      <a href='/hidden' style='display:none'>Hidden Link</a>
    </body></html>
    """


async def test_regression_sample_page_semantics(page) -> None:
    await page.set_content(_load_fixture("sample-page.html"))
    summary = await extract_page_semantics(page)

    assert summary.title == "JPetStore Demo"
    assert len(summary.forms) >= 1

    image_links = [e for e in summary.interactive_elements if e.role == "image_link"]
    map_areas = [e for e in summary.interactive_elements if e.role == "map_area"]

    assert image_links
    assert any(e.visible_text and "fish" in e.visible_text.lower() for e in image_links)
    assert map_areas
    assert {"Birds", "Fish", "Dogs", "Reptiles", "Cats"}.issubset({e.visible_text for e in map_areas})


async def test_regression_semantic_coverage(page) -> None:
    html = _coverage_fixture()
    await page.set_content(html)
    first = await extract_page_semantics(page)

    await page.reload(wait_until="load")
    await page.set_content(html)
    second = await extract_page_semantics(page)

    assert first.model_dump(mode="json") == second.model_dump(mode="json")

    assert first.title == "Semantic Coverage"
    assert first.headers == ["Checkout"]

    form = first.forms[0]
    types = {f.type for f in form.fields}
    labels = {f.label for f in form.fields}
    assert {"email", "select", "checkbox"}.issubset(types)
    assert {"Email", "Country", "Accept Terms"}.issubset(labels)
    assert all(f.type != "submit" for f in form.fields)

    options = next(f.options for f in form.fields if f.type == "select")
    assert options == ["IN", "US"]

    roles = {e.role for e in first.interactive_elements}
    assert {"link", "image_link", "map_area", "button"}.issubset(roles)

    texts = {e.visible_text for e in first.interactive_elements}
    assert "Dogs" in texts
    assert "Hidden Link" not in texts
