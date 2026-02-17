from __future__ import annotations

import json
import pytest
import time

from semantic_page_extractor import extract_page_semantics

pytest.importorskip("playwright.async_api")


def _fixture_login_page() -> str:
    return """
    <html><head><title>Login Page</title></head><body>
      <h1>Account Login</h1>
      <form>
        <label for='email'>Email</label><input id='email' type='email' required>
        <label for='password'>Password</label><input id='password' type='password'>
        <button type='submit'>Sign in</button>
      </form>
      <a href='/forgot'>Forgot password?</a>
    </body></html>
    """


def _fixture_multiple_forms() -> str:
    return """
    <html><head><title>Settings</title></head><body>
      <h1>Profile</h1>
      <form>
        <label for='name'>Name</label><input id='name' type='text'>
        <button type='submit'>Save Profile</button>
      </form>
      <h2>Security</h2>
      <form>
        <label for='otp'>OTP</label><input id='otp' type='text'>
        <button type='submit'>Save Security</button>
      </form>
    </body></html>
    """


def _fixture_hidden_elements() -> str:
    return """
    <html><head><title>Visibility Test</title></head><body>
      <h1>Visible Section</h1>
      <form>
        <label for='v1'>Visible Input</label><input id='v1' type='text'>
        <label for='h1' style='display:none'>Hidden Label</label><input id='h1' type='text' style='display:none'>
        <button type='submit'>Submit</button>
        <button type='button' style='visibility:hidden'>Ghost</button>
      </form>
      <a href='/ok'>Visible Link</a>
      <a href='/hide' style='display:none'>Hidden Link</a>
    </body></html>
    """


def _fixture_image_and_map_context() -> str:
    return """
    <html><head><title>Image Map</title></head><body>
      <div id="QuickLinks">
        <a href="/actions/Catalog.action?viewCategory=&categoryId=FISH"><img src="../images/sm_fish.gif" /></a>
      </div>
      <map name="estoremap">
        <area alt="Birds" href="/actions/Catalog.action?viewCategory=&categoryId=BIRDS" shape="RECT" />
        <area alt="Dogs" href="/actions/Catalog.action?viewCategory=&categoryId=DOGS" shape="RECT" />
      </map>
      <img src="../images/splash.gif" usemap="#estoremap" width="350" height="355" />
    </body></html>
    """


async def test_extract_simple_login_page(page) -> None:
    await page.set_content(_fixture_login_page())
    summary = await extract_page_semantics(page)

    assert summary.title == "Login Page"
    assert summary.headers == ["Account Login"]
    assert len(summary.forms) == 1
    assert len(summary.forms[0].fields) == 2
    assert any(el.role == "link" for el in summary.interactive_elements)


async def test_extract_multiple_forms(page) -> None:
    await page.set_content(_fixture_multiple_forms())
    summary = await extract_page_semantics(page)

    assert len(summary.forms) == 2
    assert summary.headers == ["Profile", "Security"]


async def test_hidden_elements_are_excluded(page) -> None:
    await page.set_content(_fixture_hidden_elements())
    summary = await extract_page_semantics(page)

    field_labels = {f.label for form in summary.forms for f in form.fields}
    texts = {e.visible_text for e in summary.interactive_elements}
    assert "Visible Input" in field_labels
    assert "Hidden Label" not in field_labels
    assert "Ghost" not in texts
    assert "Hidden Link" not in texts


async def test_image_links_and_map_areas_have_context(page) -> None:
    await page.set_content(_fixture_image_and_map_context())
    summary = await extract_page_semantics(page)

    image_links = [e for e in summary.interactive_elements if e.role == "image_link"]
    map_areas = [e for e in summary.interactive_elements if e.role == "map_area"]

    assert image_links
    assert any(e.visible_text and "fish" in e.visible_text.lower() for e in image_links)
    assert len(map_areas) == 2
    assert {"Birds", "Dogs"} == {e.visible_text for e in map_areas}
    assert any((e.section_context or "").lower() == "quicklinks" for e in image_links)


async def test_determinism_across_reload(page) -> None:
    html = _fixture_multiple_forms()
    await page.set_content(html)
    first = await extract_page_semantics(page)
    await page.reload(wait_until="load")
    await page.set_content(html)
    second = await extract_page_semantics(page)

    assert first.model_dump(mode="json") == second.model_dump(mode="json")
    assert first.page_signature == second.page_signature


async def test_output_has_no_dom_or_selector_leakage(page) -> None:
    await page.set_content(_fixture_login_page())
    summary = await extract_page_semantics(page)
    payload = json.dumps(summary.model_dump(mode="json"), sort_keys=True)

    forbidden = ["selector", "xpath", "outerHTML", "innerHTML", "documentElement"]
    assert not any(word in payload for word in forbidden)


async def test_typical_runtime_and_size(page) -> None:
    await page.set_content(_fixture_multiple_forms())
    start = time.perf_counter()
    summary = await extract_page_semantics(page)
    elapsed_ms = (time.perf_counter() - start) * 1000
    payload_size = len(json.dumps(summary.model_dump(mode="json")))

    assert elapsed_ms < 200
    assert payload_size < 15 * 1024
