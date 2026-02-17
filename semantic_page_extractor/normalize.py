from __future__ import annotations


def normalize_text(value: str | None) -> str | None:
    if value is None:
        return None
    compact = " ".join(value.split()).strip()
    return compact or None


def resolve_field_label(
    label_for: str | None,
    label_wrapped: str | None,
    aria_label: str | None,
    placeholder: str | None,
) -> str | None:
    return (
        normalize_text(label_for)
        or normalize_text(label_wrapped)
        or normalize_text(aria_label)
        or normalize_text(placeholder)
    )


def sort_key(*values: str | None) -> tuple[str, ...]:
    return tuple((v or "") for v in values)
