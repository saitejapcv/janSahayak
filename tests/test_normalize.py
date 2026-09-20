"""
Unit tests for scheme normalization and transformation.
"""

import pytest
from ingestion.normalize import (
    normalize_category,
    normalize_state_and_level,
    parse_bullet_list,
    generate_deterministic_id,
    normalize_url,
    normalize_scheme,
)


def test_category_normalization():
    # Direct canonical matches
    assert normalize_category("Education") == "Education"
    assert normalize_category("agriculture") == "Agriculture"

    # Keywords matching
    assert normalize_category("Scholarships for Students") == "Education"
    assert normalize_category("Farmer Welfare and Crop Support") == "Agriculture"
    assert normalize_category("Health, Medical Treatment") == "Healthcare"
    assert normalize_category("Women empowerment & Maternity") == "Women & Child"
    assert normalize_category("Differently Abled Persons Welfare") == "Disability"
    assert normalize_category("Old Age Pension for Senior Citizens") == "Senior Citizens"
    assert normalize_category("Skill Training and Apprenticeship") == "Employment"
    assert normalize_category("Housing Assistance and Urban Shelter") == "Housing"
    assert normalize_category("Credit Subsidy and Micro Loan") == "Financial Assistance"
    assert normalize_category("Startup and MSME Business Grant") == "Entrepreneurship"
    assert normalize_category("Tribal and Backward Classes Welfare") == "Social Welfare"

    # Unknown category maps safely to Other
    assert normalize_category("Quantum Astronomy Space Exploration") == "Other"
    assert normalize_category(None) == "Other"
    assert normalize_category("") == "Other"


def test_state_and_level_normalization():
    # Central / National
    assert normalize_state_and_level("Central") == ("All India", "Central")
    assert normalize_state_and_level("All India") == ("All India", "Central")
    assert normalize_state_and_level("all") == ("All India", "Central")
    assert normalize_state_and_level(None) == ("All India", "Central")

    # Abbreviations
    assert normalize_state_and_level("TN") == ("Tamil Nadu", "State")
    assert normalize_state_and_level("UP") == ("Uttar Pradesh", "State")
    assert normalize_state_and_level("DL") == ("Delhi", "State")
    assert normalize_state_and_level("KL") == ("Kerala", "State")
    assert normalize_state_and_level("KA") == ("Karnataka", "State")

    # Full canonical names
    assert normalize_state_and_level("Tamil Nadu") == ("Tamil Nadu", "State")
    assert normalize_state_and_level("Maharashtra") == ("Maharashtra", "State")
    assert normalize_state_and_level("Puducherry") == ("Puducherry", "State")


def test_bullet_list_parsing():
    raw_markdown = """
    - Benefit 1: Up to ₹50,000 grant
    - Benefit 2: Free textbook distribution
    * Benefit 3: Annual stipend
    1. First stage clearance
    <br>
    <strong>Additional Benefit</strong>: Mentorship access
    """
    items = parse_bullet_list(raw_markdown)
    assert len(items) == 5
    assert "Benefit 1: Up to ₹50,000 grant" in items
    assert "Benefit 2: Free textbook distribution" in items
    assert "Additional Benefit: Mentorship access" in items

    # None and empty strings should yield empty list
    assert parse_bullet_list(None) == []
    assert parse_bullet_list("") == []
    assert parse_bullet_list([]) == []


def test_deterministic_id_generation():
    # Slug based ID
    id1 = generate_deterministic_id("Test Scheme", "Tamil Nadu", slug="pm-kisan-scholarship")
    assert id1 == "SCH_PM_KISAN_SCHOLARSHIP"

    # Name + State hashing must be repeatable across calls
    id2 = generate_deterministic_id("Post Matric Scholarship", "Tamil Nadu")
    id3 = generate_deterministic_id("Post Matric Scholarship", "Tamil Nadu")
    assert id2 == id3
    assert id2.startswith("SCH_")

    # Different state should yield different ID
    id4 = generate_deterministic_id("Post Matric Scholarship", "Karnataka")
    assert id2 != id4


def test_normalize_url():
    assert normalize_url("https://scholarships.gov.in") == "https://scholarships.gov.in"
    assert normalize_url("http://example.com/apply") == "http://example.com/apply"
    assert normalize_url("null") is None
    assert normalize_url("none") is None
    assert normalize_url("") is None
    assert normalize_url("javascript:alert(1)") is None


def test_full_scheme_normalization_with_unicode():
    raw = {
        "slug": "tamil-nadu-farmer-aid",
        "name": "தமிழ்நாடு உழவர் உதவி (Tamil Nadu Farmer Aid)",
        "category": "Agriculture and Farmer Support",
        "state": "TN",
        "ministry": "Department of Agriculture, Tamil Nadu",
        "description": "Financial assistance of ₹10,000 for marginal farmers.",
        "benefits": "- ₹10,000 direct benefit transfer\n- Free soil health card",
        "eligibility_text": "- Must be a farmer\n- Land holding under 2 hectares",
        "documents_required": "- Aadhaar Card\n- Patta / Chitta document",
        "apply_url": "https://agri.tn.gov.in/apply",
        "official_url": "https://myscheme.gov.in/schemes/tamil-nadu-farmer-aid",
        "scraped_at": "2026-09-19",
    }

    norm = normalize_scheme(raw)

    assert norm["id"] == "SCH_TAMIL_NADU_FARMER_AID"
    assert "தமிழ்நாடு" in norm["name"]
    assert norm["category"] == "Agriculture"
    assert norm["state"] == "Tamil Nadu"
    assert norm["level"] == "State"
    assert norm["ministry"] == "Department of Agriculture, Tamil Nadu"
    assert len(norm["benefits"]) == 2
    assert "₹10,000" in norm["benefits"][0]
    assert len(norm["eligibility"]) == 2
    assert len(norm["required_documents"]) == 2
    assert norm["official_url"] == "https://agri.tn.gov.in/apply"
    assert norm["source_url"] == "https://myscheme.gov.in/schemes/tamil-nadu-farmer-aid"
    assert norm["last_verified"] == "2026-09-19"
    assert norm["details"] is not None
    assert norm["grievance_process"] is None
