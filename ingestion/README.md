# JanSahayak Scheme Ingestion Pipeline

Automated, legally permitted scheme data ingestion pipeline for **JanSahayak**, India's Government Benefits & Services Navigator.

---

## 1. What the Ingestion Pipeline Does

The pipeline scales JanSahayak's welfare knowledge base from a small seed list to thousands of verified central and state government schemes across India:

```
SOURCE DATASET
      ↓
FETCH (HTTP / Streaming / Local Cache)
      ↓
PARSE (CSV / Markdown lists)
      ↓
NORMALIZE (Categories, States, Stable IDs, Dates, Lists)
      ↓
DEDUPLICATE (ID & Name+State collision detection)
      ↓
VALIDATE (Strict schema adherence, URLs, non-empty fields)
      ↓
SAFEGUARD BACKUP (data/backups/schemes_<timestamp>.json)
      ↓
OUTPUT (data/schemes.json)
      ↓
S3 UPLOAD (s3://jansahayak-knowledge-406658520064/schemes.json)
```

---

## 2. What Data Source It Uses

- **Dataset**: `smartduketech/indian-government-schemes-2025` (`Schemes.csv`) hosted on Hugging Face.
- **Size**: 4,693 Indian central and state government schemes.
- **Original Provenance**: Grounded in official records from [myScheme.gov.in](https://myscheme.gov.in) (maintained by Digital India Corporation under the Ministry of Electronics and Information Technology, MeitY).
- **Attributes Preserved**: Scheme name, nodal ministry, nodal department, state/central jurisdiction, category tags, benefits, eligibility criteria, required documents, application instructions, direct application links (`apply_url`), and myScheme source references.

---

## 3. Why the Source is Permitted

- **License**: **Creative Commons Attribution 4.0 International (CC BY 4.0)**.
- **Free for Reuse**: The dataset is explicitly published under CC BY 4.0 for research, civic-tech, and public applications with attribution.
- **Zero Web Scraping**: The pipeline does **not** scrape `myScheme.gov.in`. It fetches the structured, machine-readable dataset via standard HTTP without bypassing authentication or rate-limiting safeguards.
- **Attribution**:
  > Source: SmartDuke Technologies · [schemefit.com](https://schemefit.com). Original data derived from [myScheme.gov.in](https://myscheme.gov.in).

---

## 4. How to Configure

All settings can be customized via `.env` or standard shell environment variables:

```bash
# Data source URL (or path to a local CSV file)
SCHEME_SOURCE_URL=https://huggingface.co/datasets/smartduketech/indian-government-schemes-2025/resolve/main/Schemes.csv

# AWS S3 Target Configuration
S3_BUCKET_NAME=jansahayak-knowledge-406658520064
S3_OBJECT_KEY=schemes.json
AWS_DEFAULT_REGION=us-east-1

# Networking & Timeout
REQUEST_TIMEOUT_SECONDS=45
MAX_RETRIES=3
```

---

## 5. How to Install Dependencies

We recommend using a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r ingestion/requirements.txt
```

---

## 6. How to Run Dry Run

A dry run fetches data, normalizes records, runs deduplication, and performs schema validation. It writes the result to a temporary inspection file (`data/schemes_dry_run.json`) **without** overwriting the production file or uploading to S3:

```bash
# Complete dry run
python ingestion/ingest.py --dry-run

# Quick dry run on the first 50 records
python ingestion/ingest.py --dry-run --limit 50

# Dry run filtered by Category
python ingestion/ingest.py --dry-run --category Agriculture

# Dry run filtered by State
python ingestion/ingest.py --dry-run --state "Tamil Nadu"
```

---

## 7. How to Run Production Ingestion

When ready to update the live system:

```bash
python ingestion/ingest.py
```

This will:
1. Fetch and normalize records.
2. Deduplicate against existing seed records.
3. Validate every single record.
4. Create an automatic backup in `data/backups/schemes_<timestamp>.json`.
5. Write the verified records to `data/schemes.json`.
6. Upload the new dataset to `s3://jansahayak-knowledge-406658520064/schemes.json`.

---

## 8. How S3 Upload Works

- Uses `boto3` and ambient AWS CLI/IAM credentials.
- Uploads with Content-Type `application/json; charset=utf-8`.
- If S3 upload fails due to network or IAM constraints, the local `data/schemes.json` file is preserved, a clear error message is logged, and the process exits with a non-zero exit code.

---

## 9. Expected Output Schema

Every scheme record in `data/schemes.json` strictly satisfies JanSahayak's 18-field schema:

```json
{
  "id": "SCH_PM_KISAN",
  "name": "Pradhan Mantri Kisan Samman Nidhi",
  "category": "Agriculture",
  "level": "Central",
  "state": "All India",
  "ministry": "Ministry of Agriculture and Farmers Welfare",
  "description": "Income support scheme for all landholding farmer families.",
  "details": "Under the PM-KISAN scheme, financial benefit of ₹6,000 per year...",
  "target_beneficiaries": ["Small and marginal farmers", "Landholder farmers"],
  "eligibility": ["Must own cultivable landholding in their name"],
  "exclusions": ["Institutional landholders", "Former and present holders of constitutional posts"],
  "benefits": ["₹6,000 per year in three equal installments of ₹2,000"],
  "required_documents": ["Aadhaar Card", "Land ownership papers", "Bank account details"],
  "application_process": "Online registration on the PM-KISAN portal or via Common Service Centres.",
  "grievance_process": null,
  "official_url": "https://pmkisan.gov.in/",
  "source_url": "https://www.myscheme.gov.in/schemes/pm-kisan",
  "last_verified": "2026-09-17"
}
```

---

## 10. Known Limitations

- **Source Freshness**: The dataset reflects government scheme guidelines as of the dataset collection date. For time-sensitive application deadlines, citizens should always check the official portal linked in `official_url`.
- **Application Portals**: Some state schemes do not have a dedicated online portal and must be applied for offline at district/block offices (documented in `application_process`).
- **LLM Decoupling**: Eligibility criteria are ingested strictly as factual strings. No generative AI model rewrites criteria during ingestion, eliminating hallucinations.

---

## 11. How to Add Another Permitted Data Source Later

The ingestion architecture is designed around the abstract `SchemeSource` base class in [`ingestion/sources/base.py`](file:///Users/p.c.vsaiteja/janSahayak/ingestion/sources/base.py).

To plug in a new source (e.g. `data.gov.in` OGD API):
1. Create a new file in `ingestion/sources/my_new_source.py`:
   ```python
   from .base import SchemeSource

   class MyNewSource(SchemeSource):
       def get_source_name(self) -> str:
           return "My New Permitted Source"

       def fetch_schemes(self) -> list[dict]:
           # Fetch from API or JSON
           return records
   ```
2. In `ingestion/ingest.py`, select or instantiate `MyNewSource`.
3. Pass the raw records to `normalize_scheme()`. All deduplication, validation, backup, and S3 upload steps will work automatically.
