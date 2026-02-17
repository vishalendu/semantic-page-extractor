# Semantic Page Extractor

Deterministic semantic UI extractor for Playwright pages.

## What It Does
- Extracts visible semantic/interactable elements from a loaded Playwright page.
- Returns strict Pydantic output (`PageSummary`).
- Computes deterministic signatures for fields, actions, forms, and page.

## Requirements
- Python 3.10+
- `uv` installed

## Install (uv)
```bash
uv venv
uv sync --extra dev
uv run playwright install chromium
```

## Run Tests
```bash
uv run pytest -q
```

## Standalone Usage
Use the core function with an already loaded Playwright `Page`:

```python
import asyncio
from playwright.async_api import async_playwright
from semantic_page_extractor import extract_page_semantics


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("https://example.com", wait_until="load")
        summary = await extract_page_semantics(page)
        print(summary.model_dump_json(indent=2))
        await browser.close()


asyncio.run(main())
```

## Optional URL Wrapper
```python
from semantic_page_extractor import extract_from_url

summary = await extract_from_url("https://example.com", wait_until="load")
```

## Local Example
```bash
uv run python examples/standalone_example.py
```

## URL Extractor Example Script
`examples/extract_from_url.py` supports full extraction, actionable dedup, intent filtering, and compact output.

Base usage:
```bash
uv run python examples/extract_from_url.py "https://example.com"
```

Actionable-only (deduped):
```bash
uv run python examples/extract_from_url.py "https://example.com" --actionable-only
```

Intent filtering:
```bash
uv run python examples/extract_from_url.py "https://example.com" --intent "add to cart" --min-score 0.55 --max-results 20
```

Intent + actionable-only (intent first, then dedup):
```bash
uv run python examples/extract_from_url.py "https://example.com" --intent "add to cart" --actionable-only
```

Minified output:
```bash
uv run python examples/extract_from_url.py "https://example.com" --actionable-only --minify
```

Output format options:
- default (no `--output-format`): full payload fields
- `--output-format json`: strips `action_signature` and `disabled` fields
- `--output-format compact`: compact indexed payload for lower token/size cost

Examples:
```bash
uv run python examples/extract_from_url.py "https://example.com" --intent "add to cart" --actionable-only --output-format json --minify
```

```bash
uv run python examples/extract_from_url.py "https://example.com" --intent "add to cart" --actionable-only --output-format compact --minify
```

## Public API
- `extract_page_semantics(page) -> PageSummary`
- `extract_from_url(url, wait_until="load") -> PageSummary`
- `extract_actionable_elements(summary) -> list[InteractiveElement]` (deduped merge of form submit actions + global interactables)
- `ExtractionError`
