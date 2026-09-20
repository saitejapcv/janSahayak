"""
Validation module for JanSahayak scheme records.
Ensures only high-quality, conforming records enter the production dataset.
"""

import re
from typing import List, Dict, Any, Tuple
from .config import VALID_CATEGORIES

from urllib.parse import urlparse

def is_valid_url(url: str) -> bool:
    """Validates URL structure including international and punycode domains."""
    if not url or not isinstance(url, str):
        return False
    try:
        parsed = urlparse(url)
        return parsed.scheme in ["http", "https"] and bool(parsed.netloc)
    except Exception:
        return False

DATE_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def validate_scheme(scheme: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validates a single scheme record against JanSahayak schema constraints.
    
    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_error_messages)
    """
    errors = []

    # 1. ID check
    scheme_id = scheme.get("id")
    if not scheme_id or not str(scheme_id).strip():
        errors.append("Missing or empty 'id'")

    # 2. Name check
    name = scheme.get("name")
    if not name or not str(name).strip() or len(str(name).strip()) < 3:
        errors.append("Missing, empty, or too short 'name'")

    # 3. Category check
    category = scheme.get("category")
    if not category or category not in VALID_CATEGORIES:
        errors.append(f"Invalid category '{category}'; must be one of {VALID_CATEGORIES}")

    # 4. Description check
    description = scheme.get("description")
    if not description or not str(description).strip():
        errors.append("Missing or empty 'description'")

    # 5. List type checks
    list_fields = [
        "target_beneficiaries",
        "eligibility",
        "exclusions",
        "benefits",
        "required_documents",
    ]
    for field in list_fields:
        val = scheme.get(field)
        if val is not None and not isinstance(val, list):
            errors.append(f"Field '{field}' must be a list, got {type(val).__name__}")

    # 6. Must have at least one of eligibility or benefits
    eligibility = scheme.get("eligibility") or []
    benefits = scheme.get("benefits") or []
    if not eligibility and not benefits:
        errors.append("Both 'eligibility' and 'benefits' are empty; record lacks essential content")

    # 7. URL checks if provided
    for url_field in ["official_url", "source_url"]:
        url_val = scheme.get(url_field)
        if url_val is not None:
            if not is_valid_url(url_val):
                errors.append(f"Invalid URL in '{url_field}': {url_val}")

    # 8. Date check
    last_verified = scheme.get("last_verified")
    if last_verified and not DATE_REGEX.match(str(last_verified)):
        errors.append(f"Invalid date format in 'last_verified': '{last_verified}', expected YYYY-MM-DD")

    return (len(errors) == 0, errors)


def validate_dataset(schemes: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Tuple[Dict[str, Any], List[str]]]]:
    """
    Validates a list of scheme records.
    Also ensures no duplicate IDs exist within the validated batch.
    
    Returns:
        Tuple: (valid_records, rejected_records_with_reasons)
    """
    valid = []
    rejected = []
    seen_ids = set()

    for scheme in schemes:
        is_valid, errors = validate_scheme(scheme)
        scheme_id = scheme.get("id")

        if is_valid:
            if scheme_id in seen_ids:
                rejected.append((scheme, [f"Duplicate scheme ID: '{scheme_id}'"]))
            else:
                seen_ids.add(scheme_id)
                valid.append(scheme)
        else:
            rejected.append((scheme, errors))

    return valid, rejected
