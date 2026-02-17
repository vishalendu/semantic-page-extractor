from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))


@pytest.fixture
async def page():
    playwright = pytest.importorskip("playwright.async_api")
    async with playwright.async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        try:
            yield page
        finally:
            await browser.close()
