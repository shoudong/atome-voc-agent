"""Deduplication logic for crawled posts."""

import hashlib


def content_hash(text: str) -> str:
    """Generate a normalized hash for near-duplicate detection."""
    normalized = text.lower().strip()
    # Remove common noise
    for char in [".", ",", "!", "?", "#", "@"]:
        normalized = normalized.replace(char, "")
    normalized = " ".join(normalized.split())
    return hashlib.sha256(normalized.encode()).hexdigest()[:16]


def is_too_short(text: str, min_chars: int = 30) -> bool:
    """Discard posts shorter than threshold."""
    return len(text.strip()) < min_chars


def mentions_brand(text: str, brand_terms: list[str] | None = None) -> bool:
    """Check if text mentions Atome or configured brand terms."""
    if brand_terms is None:
        brand_terms = ["atome", "atome ph", "atome_ph", "@atome_ph"]
    lower = text.lower()
    return any(term in lower for term in brand_terms)


def is_official_account(handle: str) -> bool:
    """Discard posts from official brand accounts."""
    official = {"atome_ph", "atomeph", "atomeapp"}
    return handle.lower().strip("@") in official
