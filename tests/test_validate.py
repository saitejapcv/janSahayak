"""
Unit tests for scheme validation, deduplication, and error handling.
"""

import pytest
from pathlib import Path
from ingestion.validate import validate_scheme, validate_dataset
from ingestion.deduplicate import deduplicate_schemes
from ingestion.s3_uploader import upload_schemes_to_s3


@pytest.fixture
def sample_valid_scheme():
    return {
        "id": "EDU004",
        "name": "PM-USP Central Sector Scheme of Scholarship",
        "category": "Education",
        "level": "Central",
        "state": "All India",
        "ministry": "Ministry of Education",
        "description": "Scholarship assistance for college students.",
        "details": "Full details on the PM-USP scholarship.",
        "target_beneficiaries": ["Meritorious students"],
        "eligibility": ["Class 12 board percentile > 80%"],
        "exclusions": ["Distance education students"],
        "benefits": ["Financial assistance"],
        "required_documents": ["12th Marksheet"],
        "application_process": "Apply via National Scholarships Portal.",
        "grievance_process": None,
        "official_url": "https://scholarships.gov.in/",
        "source_url": "https://www.myscheme.gov.in/schemes/csss-cus",
        "last_verified": "2026-09-17",
    }


def test_valid_scheme_passes(sample_valid_scheme):
    is_valid, errors = validate_scheme(sample_valid_scheme)
    assert is_valid is True
    assert len(errors) == 0


def test_missing_required_fields(sample_valid_scheme):
    # Missing ID
    bad_scheme = dict(sample_valid_scheme)
    bad_scheme["id"] = ""
    is_valid, errors = validate_scheme(bad_scheme)
    assert is_valid is False
    assert any("id" in err.lower() for err in errors)

    # Missing Name
    bad_scheme = dict(sample_valid_scheme)
    bad_scheme["name"] = None
    is_valid, errors = validate_scheme(bad_scheme)
    assert is_valid is False
    assert any("name" in err.lower() for err in errors)

    # Missing Description
    bad_scheme = dict(sample_valid_scheme)
    bad_scheme["description"] = "   "
    is_valid, errors = validate_scheme(bad_scheme)
    assert is_valid is False
    assert any("description" in err.lower() for err in errors)


def test_invalid_category(sample_valid_scheme):
    bad_scheme = dict(sample_valid_scheme)
    bad_scheme["category"] = "InvalidFakeCategory"
    is_valid, errors = validate_scheme(bad_scheme)
    assert is_valid is False
    assert any("category" in err.lower() for err in errors)


def test_invalid_list_types(sample_valid_scheme):
    bad_scheme = dict(sample_valid_scheme)
    bad_scheme["eligibility"] = "Not a list, a string"
    is_valid, errors = validate_scheme(bad_scheme)
    assert is_valid is False
    assert any("eligibility" in err for err in errors)


def test_invalid_url_and_date(sample_valid_scheme):
    bad_scheme = dict(sample_valid_scheme)
    bad_scheme["official_url"] = "not-a-valid-url"
    bad_scheme["last_verified"] = "17-09-2026"  # wrong format, should be YYYY-MM-DD
    is_valid, errors = validate_scheme(bad_scheme)
    assert is_valid is False
    assert any("official_url" in err for err in errors)
    assert any("last_verified" in err for err in errors)


def test_deduplication():
    records = [
        {"id": "SCH_001", "name": "Scholarship A", "state": "Tamil Nadu", "category": "Education", "benefits": ["B1"]},
        {"id": "SCH_002", "name": "Scholarship B", "state": "Tamil Nadu", "category": "Education", "benefits": ["B2"]},
        {"id": "SCH_001", "name": "Scholarship A (Duplicate)", "state": "Tamil Nadu", "category": "Education", "benefits": ["B1"]},
        {"id": "SCH_003", "name": "Scholarship A", "state": "Tamil Nadu", "category": "Education", "benefits": ["B1"]},
    ]

    unique, dup_count = deduplicate_schemes(records)
    assert len(unique) == 2
    assert dup_count == 2
    assert unique[0]["id"] == "SCH_001"
    assert unique[1]["id"] == "SCH_002"


def test_dataset_validation_with_duplicates(sample_valid_scheme):
    records = [
        sample_valid_scheme,
        dict(sample_valid_scheme),  # Exact duplicate ID
    ]
    valid, rejected = validate_dataset(records)
    assert len(valid) == 1
    assert len(rejected) == 1
    assert "Duplicate scheme ID" in rejected[0][1][0]


def test_s3_upload_non_existent_file():
    fake_path = Path("/path/does/not/exist/schemes.json")
    success = upload_schemes_to_s3(fake_path, bucket_name="nonexistent-bucket-12345")
    assert success is False
