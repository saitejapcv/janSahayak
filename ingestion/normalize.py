"""
Normalization logic for JanSahayak scheme records.
Transforms raw source records into the standard JanSahayak schema.
"""

import re
import hashlib
from datetime import datetime, date
from typing import Dict, Any, List, Optional

from .config import VALID_CATEGORIES, CANONICAL_STATES

# State mapping lookup for common abbreviations and variants
STATE_ALIASES = {
    "tn": "Tamil Nadu",
    "tamil nadu state": "Tamil Nadu",
    "up": "Uttar Pradesh",
    "uttar pradesh state": "Uttar Pradesh",
    "ap": "Andhra Pradesh",
    "andhra pradesh state": "Andhra Pradesh",
    "mp": "Madhya Pradesh",
    "madhya pradesh state": "Madhya Pradesh",
    "wb": "West Bengal",
    "west bengal state": "West Bengal",
    "mh": "Maharashtra",
    "maharashtra state": "Maharashtra",
    "ka": "Karnataka",
    "karnataka state": "Karnataka",
    "kl": "Kerala",
    "kerala state": "Kerala",
    "ts": "Telangana",
    "telangana state": "Telangana",
    "dl": "Delhi",
    "delhi nct": "Delhi",
    "nct of delhi": "Delhi",
    "all india": "All India",
    "all": "All India",
    "central": "All India",
    "national": "All India",
    "pan india": "All India",
    "py": "Puducherry",
    "pondicherry": "Puducherry",
    "orissa": "Odisha",
    "uttaranchal": "Uttarakhand",
    "jk": "Jammu and Kashmir",
    "j&k": "Jammu and Kashmir",
}


def normalize_category(raw_category: Optional[str]) -> str:
    """
    Normalizes a category string into the JanSahayak canonical vocabulary:
    Education, Agriculture, Healthcare, Employment, Housing, Women & Child,
    Disability, Senior Citizens, Financial Assistance, Entrepreneurship,
    Social Welfare, Other.
    """
    if not raw_category or not str(raw_category).strip():
        return "Other"

    cat = str(raw_category).strip().lower()

    # Direct match against canonical names
    for valid_cat in VALID_CATEGORIES:
        if cat == valid_cat.lower():
            return valid_cat

    # Keyword heuristics based on standard government scheme classifications
    if any(k in cat for k in ["disability", "differently abled", "pwd", "handicap"]):
        return "Disability"
    if any(k in cat for k in ["senior citizen", "elderly", "old age", "pension"]):
        return "Senior Citizens"
    if any(k in cat for k in ["women", "girl", "child", "maternal", "maternity", "infant"]):
        return "Women & Child"
    if any(k in cat for k in ["education", "scholarship", "student", "fellowship", "academic", "school", "college"]):
        return "Education"
    if any(k in cat for k in ["agriculture", "farmer", "crop", "irrigation", "fisher", "horticulture", "dairy", "animal husbandry"]):
        return "Agriculture"
    if any(k in cat for k in ["health", "medical", "disease", "treatment", "hospital", "ayushman"]):
        return "Healthcare"
    if any(k in cat for k in ["housing", "shelter", "awas"]):
        return "Housing"
    if any(k in cat for k in ["employment", "job", "livelihood", "skill", "training", "vocational", "unemployment", "labour", "worker"]):
        return "Employment"
    if any(k in cat for k in ["entrepreneur", "business", "startup", "msme", "industry", "commerce", "trade"]):
        return "Entrepreneurship"
    if any(k in cat for k in ["financial assistance", "credit", "subsidy", "loan", "grant", "banking"]):
        return "Financial Assistance"
    if any(k in cat for k in ["social welfare", "tribal", "backward", "sc/st", "minority", "empowerment", "caste"]):
        return "Social Welfare"

    return "Other"


def normalize_state_and_level(raw_state: Optional[str]) -> tuple[str, str]:
    """
    Normalizes state and determines jurisdiction level (Central vs State).
    
    Returns:
        tuple[str, str]: (normalized_state, level)
    """
    if not raw_state or not str(raw_state).strip():
        return "All India", "Central"

    st_clean = str(raw_state).strip()
    st_lower = st_clean.lower()

    # Check alias dictionary
    if st_lower in STATE_ALIASES:
        normalized = STATE_ALIASES[st_lower]
        level = "Central" if normalized == "All India" else "State"
        return normalized, level

    # Check canonical state list case-insensitively
    for canon in CANONICAL_STATES:
        if st_lower == canon.lower():
            level = "Central" if canon == "All India" else "State"
            return canon, level

    # If it contains "central"
    if "central" in st_lower or "india" in st_lower:
        return "All India", "Central"

    # Default to preserving stripped title case if unrecognized state string
    return st_clean.title(), "State"


def parse_bullet_list(raw_value: Any) -> List[str]:
    """
    Converts markdown, bullet points, newline-separated or JSON list strings into a clean List[str].
    Removes HTML tags, leading markdown bullets, and empty lines.
    """
    if not raw_value:
        return []

    if isinstance(raw_value, list):
        return [str(item).strip() for item in raw_value if item and str(item).strip()]

    text = str(raw_value)
    # Convert block tags like <br>, <p>, <li> to newlines
    text = re.sub(r"<(?:br|p|li|div|h\d)[^>]*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</(?:p|li|div|h\d)>", "\n", text, flags=re.IGNORECASE)
    # Strip remaining inline tags like <strong>, <em>, <span>, <b>, <a>
    text = re.sub(r"<[^>]+>", "", text)

    lines = text.split("\n")
    results = []

    for line in lines:
        cleaned = line.strip()
        # Remove markdown bullets: '-', '*', '>', or numbered '1.', '2)'
        cleaned = re.sub(r"^[\s\*\-\•\>\–\—]+", "", cleaned)
        cleaned = re.sub(r"^\d+[\.\)]\s*", "", cleaned)
        cleaned = cleaned.strip()

        # Skip headers like "### Eligibility" or empty lines
        if cleaned.startswith("#") or len(cleaned) < 2:
            continue

        results.append(cleaned)

    # If splitting by newline gave nothing but text exists, return text as single item
    if not results and text.strip():
        clean_text = re.sub(r"^[\s\*\-\•\>\–\—]+", "", text.strip())
        if clean_text:
            results.append(clean_text)

    return results


def generate_deterministic_id(name: str, state: str, slug: Optional[str] = None) -> str:
    """
    Generates a deterministic and stable scheme ID.
    Prioritizes official slug if provided; otherwise hashes name and state.
    """
    if slug and str(slug).strip():
        clean_slug = re.sub(r"[^A-Za-z0-9_]", "_", str(slug).strip().upper())
        clean_slug = re.sub(r"_+", "_", clean_slug).strip("_")
        return f"SCH_{clean_slug[:40]}"

    # Hash name + state
    key = f"{name.strip().lower()}|{state.strip().lower()}"
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:8].upper()
    return f"SCH_{digest}"


def normalize_url(url: Optional[str]) -> Optional[str]:
    """Ensures URL has a valid scheme and clean formatting or returns None."""
    if not url or str(url).strip().lower() in ["null", "none", "n/a", ""]:
        return None
    cleaned = str(url).strip().rstrip("?#")
    if cleaned.startswith("http://") or cleaned.startswith("https://"):
        return cleaned
    return None


def normalize_date(date_val: Optional[str]) -> str:
    """Extracts or normalizes date to YYYY-MM-DD format."""
    if not date_val or str(date_val).strip().lower() in ["null", "none", ""]:
        return date.today().isoformat()

    val_str = str(date_val).strip()
    # Match YYYY-MM-DD
    match = re.search(r"\b(\d{4})-(\d{2})-(\d{2})\b", val_str)
    if match:
        return match.group(0)

    try:
        dt = datetime.fromisoformat(val_str.replace("Z", "+00:00"))
        return dt.date().isoformat()
    except Exception:
        return date.today().isoformat()


def normalize_scheme(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transforms a raw scheme dictionary into the strict JanSahayak schema:
    {
      "id": "...",
      "name": "...",
      "category": "...",
      "level": "Central" | "State",
      "state": "...",
      "ministry": "...",
      "description": "...",
      "details": "...",
      "target_beneficiaries": [],
      "eligibility": [],
      "exclusions": [],
      "benefits": [],
      "required_documents": [],
      "application_process": "...",
      "grievance_process": "...",
      "official_url": "...",
      "source_url": "...",
      "last_verified": "YYYY-MM-DD"
    }
    """
    # 1. Scheme Name
    name = (raw.get("name") or raw.get("title") or raw.get("scheme_name") or "").strip()

    # 2. State & Level
    raw_state = raw.get("state") or raw.get("eligibility_state") or raw.get("level")
    norm_state, norm_level = normalize_state_and_level(raw_state)

    # 3. Category
    raw_cat = raw.get("category") or raw.get("tags")
    norm_category = normalize_category(raw_cat)

    # 4. ID
    raw_id = raw.get("id") or raw.get("scheme_id")
    slug = raw.get("slug")
    if raw_id and str(raw_id).strip():
        scheme_id = str(raw_id).strip()
    else:
        scheme_id = generate_deterministic_id(name, norm_state, slug)

    # 5. Ministry & Department
    ministry = raw.get("ministry")
    department = raw.get("department")
    ministry_clean = None
    if ministry and str(ministry).strip() and str(ministry).lower() != "null":
        ministry_clean = str(ministry).strip()
    elif department and str(department).strip() and str(department).lower() != "null":
        ministry_clean = str(department).strip()

    # 6. Description & Details
    description = raw.get("description") or raw.get("brief") or raw.get("short_description")
    description_clean = str(description).strip() if description and str(description).strip() else None

    details = raw.get("details") or raw.get("full_description") or description_clean
    details_clean = str(details).strip() if details and str(details).strip() else None

    # 7. Lists
    target_beneficiaries = parse_bullet_list(raw.get("target_beneficiaries") or raw.get("beneficiary_type"))
    eligibility = parse_bullet_list(raw.get("eligibility") or raw.get("eligibility_text") or raw.get("criteria"))
    exclusions = parse_bullet_list(raw.get("exclusions") or raw.get("ineligibility"))
    benefits = parse_bullet_list(raw.get("benefits") or raw.get("benefit"))
    required_documents = parse_bullet_list(raw.get("required_documents") or raw.get("documents_required") or raw.get("documents"))

    # 8. Application & Grievance Process
    app_process = raw.get("application_process") or raw.get("how_to_apply")
    app_process_clean = str(app_process).strip() if app_process and str(app_process).strip() else None

    grievance = raw.get("grievance_process")
    grievance_clean = str(grievance).strip() if grievance and str(grievance).strip() else None

    # 9. URLs
    # apply_url is typically the direct government portal; official_url in CSV is myscheme source
    apply_url = raw.get("apply_url") or raw.get("portal_url") or raw.get("official_url")
    official_url_clean = normalize_url(apply_url)

    source_url = raw.get("source_url") or raw.get("official_url")
    if not source_url and slug:
        source_url = f"https://www.myscheme.gov.in/schemes/{slug}"
    source_url_clean = normalize_url(source_url)

    # 10. Date
    last_verified = normalize_date(raw.get("last_verified") or raw.get("scraped_at") or raw.get("updated_at"))

    return {
        "id": scheme_id,
        "name": name,
        "category": norm_category,
        "level": norm_level,
        "state": norm_state,
        "ministry": ministry_clean,
        "description": description_clean,
        "details": details_clean,
        "target_beneficiaries": target_beneficiaries,
        "eligibility": eligibility,
        "exclusions": exclusions,
        "benefits": benefits,
        "required_documents": required_documents,
        "application_process": app_process_clean,
        "grievance_process": grievance_clean,
        "official_url": official_url_clean,
        "source_url": source_url_clean,
        "last_verified": last_verified,
    }
