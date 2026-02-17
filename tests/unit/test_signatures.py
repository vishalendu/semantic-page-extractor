from semantic_page_extractor.signatures import action_signature, field_signature, sha256_canonical


def test_signature_stability() -> None:
    left = field_signature("Email", "email", "Login")
    right = field_signature("Email", "email", "Login")
    assert left == right


def test_basic_collision_sanity() -> None:
    assert action_signature("Submit", "button", "Login") != action_signature("Cancel", "button", "Login")


def test_canonical_hash_is_order_independent() -> None:
    a = sha256_canonical({"b": 2, "a": 1})
    b = sha256_canonical({"a": 1, "b": 2})
    assert a == b
