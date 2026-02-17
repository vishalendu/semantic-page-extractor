# Semantic Page Extractor v1 TODOs

## Design Constraints (Must Hold)
- [ ] Keep modules small and single-purpose (no monolithic extractor file).
- [ ] Prefer composition of tiny helpers over large classes.
- [ ] Minimize LOC by sharing normalization/hash/sort utilities.
- [ ] Stay strictly within v1 spec; avoid optional abstractions unless needed.
- [ ] Keep public API minimal (`extract_page_semantics`, optional `extract_from_url`).
- [ ] Do not build any server, API endpoint, daemon, or CLI runtime in v1.
- [ ] Prioritize "works correctly as standalone function call" before any enhancements.

## 1) Project Setup
- [ ] Create Python package layout (`semantic_page_extractor/`).
- [ ] Add dependency setup for `playwright`, `pydantic`, `pytest`, `pytest-asyncio`.
- [ ] Add basic test configuration (`pytest.ini` or equivalent).
- [ ] Keep package surface minimal (only required modules exported).
- [ ] Add a tiny local example script that calls the extractor function directly.

## 2) Schema Models (Pydantic)
- [ ] Implement `InteractiveElement` model exactly per spec fields.
- [ ] Implement `FieldSummary` model exactly per spec fields.
- [ ] Implement `FormSummary` model exactly per spec fields.
- [ ] Implement `PageSummary` model exactly per spec fields.
- [ ] Ensure model serialization is deterministic (stable key ordering path).
- [ ] Keep schemas in one focused module without business logic.

## 3) Core Extraction API
- [ ] Implement `async def extract_page_semantics(page) -> PageSummary`.
- [ ] Use browser-context extraction via `page.evaluate(JS_SCRIPT)`.
- [ ] Add optional wrapper `extract_from_url(url, wait_until="load")` only if it helps quick local verification.
- [ ] Keep API layer thin: orchestrate only, no duplicated parsing logic.

## 4) Browser-Side Extraction Rules
- [ ] Collect only required element classes:
  - [ ] `input`, `textarea`, `select`, `button`, `a[href]`, `[role="button"]`, image links (`a > img`).
- [ ] Exclude non-semantic nodes (`div`/`span` without role, decorative elements).
- [ ] Apply visibility filters:
  - [ ] Exclude hidden/detached/non-rendered nodes (`display:none`, `visibility:hidden`, no layout box).
  - [ ] Include disabled controls but mark `disabled=True`.
- [ ] Ignore iframe traversal in v1.
- [ ] Keep JS payload compact and purpose-built (semantic data only, no DOM dump).

## 5) Semantic Enrichment
- [ ] Implement field label resolution priority:
  - [ ] `<label for="...">`
  - [ ] wrapping `<label>`
  - [ ] `aria-label`
  - [ ] `placeholder` fallback
- [ ] Compute `section_context` using nearest `h1/h2/h3/legend`.
- [ ] Extract form-level data:
  - [ ] fields
  - [ ] submit buttons
  - [ ] section context
- [ ] Centralize text normalization in one helper used by all enrichers.

## 6) Deterministic Signatures
- [ ] Implement SHA256 utility for canonical semantic payloads.
- [ ] `field_signature` from normalized label + input type + section context.
- [ ] `action_signature` from normalized visible text + role + section context.
- [ ] `form_signature` deterministic from form semantic content.
- [ ] `page_signature` from title + sorted headers + form count + interactive element count.
- [ ] Ensure lists are sorted before hashing and output.
- [ ] Reuse one canonical serializer for all signature inputs.

## 7) Validation and Errors
- [ ] Validate final payload strictly through Pydantic before returning.
- [ ] Add structured extraction exception type for failures.
- [ ] Handle empty/no-form pages without failure.
- [ ] Handle SPA timing assumptions via `wait_until` support path.
- [ ] Keep error model small (single typed exception + concise error payload).

## 8) Unit Tests
- [ ] Test label resolution precedence.
- [ ] Test disabled detection behavior.
- [ ] Test signature stability for same semantic input.
- [ ] Add basic hash collision sanity test (different semantics => different hashes).
- [ ] Keep tests table-driven where possible to reduce repetition.

## 9) Integration Tests (Real Playwright Browser)
- [ ] Test simple login page extraction.
- [ ] Test page with multiple forms.
- [ ] Test page with hidden elements excluded.
- [ ] Test determinism across page reload.
- [ ] Confirm no selector identity leakage in output.
- [ ] Confirm no full DOM leakage in output.
- [ ] Reuse shared HTML fixtures/helpers to avoid duplicated setup code.

## 10) Non-Functional Verification
- [ ] Add check/benchmark helper for typical extraction runtime target (<200ms excluding load).
- [ ] Add check for typical output size target (<15KB).
- [ ] Confirm no global mutable state is used.
- [ ] Keep performance checks lightweight (no heavy benchmarking framework).

## 11) Definition of Done Gate
- [ ] Schema validates extractor output.
- [ ] Deterministic signatures confirmed by tests.
- [ ] Integration tests pass in real browser.
- [ ] Output stable across reload.
- [ ] No DOM leakage and no selector-based identity.
- [ ] Implementation remains compact and modular with no unnecessary files.

## 12) Intent Filter for Actionable Elements
- [x] Add deterministic searchable-text builder for actionable elements (`visible_text`, `aria_label`, `section_context`, `role`).
- [x] Add deterministic ranking function for intent query with exact/token/fuzzy scoring.
- [x] Add filtering function with `min_score` and optional `max_results`.
- [x] Add summary-level helper that chains dedup actionable extraction + intent filter.
- [x] Add unit tests for:
  - [x] exact match ranking
  - [x] fuzzy typo tolerance
  - [x] multi-property matching (e.g., section context)
  - [x] deterministic ordering for ties
- [x] Add regression test using `out.json` for query `"add to cart"`.
- [x] Add example usage path in `examples/extract_from_url.py`.
