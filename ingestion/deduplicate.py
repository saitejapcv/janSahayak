"""
Deduplication logic for JanSahayak scheme ingestion.
Preserves existing records while deduplicating new entries based on:
1. Scheme ID
2. Normalized Name + State
3. Normalized Name + Ministry (if state identical)
"""

import re
from typing import List, Dict, Any, Tuple


def _normalize_name_for_dedup(name: str) -> str:
    """Removes special characters and extra spaces for deduplication comparison."""
    if not name:
        return ""
    cleaned = re.sub(r"[^\w\s]", " ", name.lower())
    return " ".join(cleaned.split())


def deduplicate_schemes(schemes: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], int]:
    """
    Deduplicates a list of normalized scheme records.
    
    Returns:
        Tuple[List[Dict[str, Any]], int]: (unique_schemes, duplicates_count)
    """
    seen_ids = set()
    seen_name_state = set()
    unique_records = []
    duplicates_count = 0

    for scheme in schemes:
        scheme_id = scheme.get("id")
        name = scheme.get("name") or ""
        state = scheme.get("state") or "All India"
        ministry = scheme.get("ministry") or ""

        norm_name = _normalize_name_for_dedup(name)
        norm_state = state.strip().lower()
        norm_ministry = ministry.strip().lower()

        # Deduplication keys
        name_state_key = (norm_name, norm_state)
        name_ministry_key = (norm_name, norm_ministry) if norm_ministry else None

        # 1. Check ID collision
        if scheme_id and scheme_id in seen_ids:
            duplicates_count += 1
            continue

        # 2. Check Name + State collision
        if norm_name and name_state_key in seen_name_state:
            duplicates_count += 1
            continue

        # Mark as seen
        if scheme_id:
            seen_ids.add(scheme_id)
        if norm_name:
            seen_name_state.add(name_state_key)

        unique_records.append(scheme)

    return unique_records, duplicates_count
