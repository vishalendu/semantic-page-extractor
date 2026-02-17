from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class InteractiveElement(BaseModel):
    action_signature: str
    role: str
    visible_text: str | None
    aria_label: str | None
    disabled: bool
    section_context: str | None

    model_config = ConfigDict(extra="forbid")


class FieldSummary(BaseModel):
    field_signature: str
    label: str | None
    type: str
    required: bool
    placeholder: str | None
    options: list[str] | None
    disabled: bool

    model_config = ConfigDict(extra="forbid")


class FormSummary(BaseModel):
    form_signature: str
    section_context: str | None
    fields: list[FieldSummary]
    submit_buttons: list[InteractiveElement]

    model_config = ConfigDict(extra="forbid")


class PageSummary(BaseModel):
    schema_version: str
    url: str
    title: str
    page_signature: str
    headers: list[str]
    forms: list[FormSummary]
    interactive_elements: list[InteractiveElement]

    model_config = ConfigDict(extra="forbid")
