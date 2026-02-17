SPEC — Semantic Page Extractor (Python + Playwright)
1. Purpose
Given a loaded Playwright Page, return a deterministic JSON structure containing all visible, interactable, semantic UI elements.
This function must:
* Be deterministic
* Be schema-validated
* Not return full DOM
* Not include CSS selectors as identity
* Not depend on XPath

2. Function Signature
async def extract_page_semantics(page: playwright.async_api.Page) -> PageSummary
Optional future wrapper:
async def extract_from_url(url: str, wait_until: str = "load") -> PageSummary

3. Output Model (Strict Schema)
Use Pydantic for validation.
class PageSummary(BaseModel):
    schema_version: str
    url: str
    title: str
    page_signature: str
    headers: List[str]
    forms: List[FormSummary]
    interactive_elements: List[InteractiveElement]

3.1 FormSummary
class FormSummary(BaseModel):
    form_signature: str
    section_context: Optional[str]
    fields: List[FieldSummary]
    submit_buttons: List[InteractiveElement]

3.2 FieldSummary
class FieldSummary(BaseModel):
    field_signature: str
    label: Optional[str]
    type: str  # text, email, password, checkbox, radio, select, textarea, etc.
    required: bool
    placeholder: Optional[str]
    options: Optional[List[str]]  # for select/radio
    disabled: bool

3.3 InteractiveElement
class InteractiveElement(BaseModel):
    action_signature: str
    role: str  # button, link, image_link, pagination, etc.
    visible_text: Optional[str]
    aria_label: Optional[str]
    disabled: bool
    section_context: Optional[str]

4. Extraction Rules
Extraction must occur inside browser context using:
page.evaluate(JS_SCRIPT)
or accessibility snapshot.

4.1 Include Only Visible + Enabled Elements
Criteria:
* offsetParent != null
* visibility != hidden
* display != none
* Not detached from DOM
Ignore:
* Hidden elements
* Disabled inputs (but include with disabled=True)
* Elements outside viewport only if visible in DOM

4.2 Extract Element Types
Must include:
* input
* textarea
* select
* button
* a[href]
* elements with role="button"
* image links (img inside anchor)
Do NOT include:
* div without role
* span without role
* purely decorative elements

4.3 Label Resolution
For input fields:
Resolve label using:
1. <label for="">
2. Wrapping <label>
3. aria-label
4. placeholder fallback

4.4 Section Context
Determine nearest:
* h1
* h2
* h3
* legend (for fieldsets)
Used for signature stability.

5. Signature Generation Rules
Signatures must be deterministic SHA256 of semantic attributes only.
5.1 Page Signature
Hash of:
* title
* sorted headers
* count of forms
* count of interactive elements
Do NOT hash URL alone.

5.2 Field Signature
Hash of:
* normalized label
* input type
* section_context

5.3 Action Signature
Hash of:
* normalized visible_text
* role
* section_context

6. Determinism Requirements
* Lists must be sorted before hashing
* JSON keys must be ordered
* No random UUIDs
* No timestamps
* Same page → same PageSummary hash

7. Non-Functional Constraints
* Execution time under 200ms for typical page (excluding page load)
* Output size < 15KB typical page
* No global state
* No LLM usage
* No graph mutation

8. Error Handling
Must handle:
* Iframe presence (ignore in v1)
* Pages with no forms
* Pages with dynamic SPA rendering (require wait_until option)
Raise structured exception if extraction fails.

9. Testing Requirements
Unit Tests
* Label resolution logic
* Signature stability
* Hash collision detection (basic)
* Disabled detection
Integration Tests (Real Browser)
* Extract simple login page
* Extract page with multiple forms
* Extract page with hidden elements
* Verify determinism across reload
Must launch real Playwright browser.
No mocks allowed for integration tests.

10. Out of Scope
* Navigation
* Recording
* Graph building
* LLM
* Session memory
* State machine
* Execution engine

Definition of Done
Extractor is complete when:
* Pydantic schema validates output
* Deterministic signatures confirmed
* Integration tests pass
* Output JSON stable across reload
* No DOM leakage
* No selectors stored as identity


