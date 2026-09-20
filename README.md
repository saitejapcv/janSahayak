# JanSahayak (जनसहायक)

> **Government Benefits, Simplified.**  
> An intelligent government benefits and scheme discovery assistant for Indian citizens, built on Amazon Web Services (AWS) for the **WeMakeDevs AWS First Commit Hackathon**.

[![AWS Architecture](https://img.shields.io/badge/AWS-Serverless-orange.svg?logo=amazon-aws)](https://aws.amazon.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Vite](https://img.shields.io/badge/Frontend-React_19_+_Vite_6-61dafb.svg?logo=react)](https://vitejs.dev/)
[![Live API](https://img.shields.io/badge/API_Gateway-Live-green.svg)](https://ddf6zddofk.execute-api.us-east-1.amazonaws.com/search)

---

## Table of Contents
1. [Problem](#problem)
2. [Solution](#solution)
3. [Key Features](#features)
4. [Architecture](#architecture)
5. [AWS Services Used](#aws-services)
6. [How It Works](#how-it-works)
7. [API Specification](#api)
8. [Local Setup](#local-setup)
9. [Deployment](#deployment)
10. [Data & Ingestion Pipeline](#data)
11. [Amazon Bedrock Status & Graceful Fallback](#bedrock-status)
12. [What I Learned](#what-i-learned)
13. [Challenges & Solutions](#challenges)
14. [Future Roadmap](#future-roadmap)
15. [Demo Video & Resources](#demo)
16. [License](#license)

---

## Problem

India administers thousands of welfare programs, scholarships, healthcare subsidies, and grants across central ministries and 28+ states. However, citizens face systemic friction when trying to discover and claim them:
- **Information Fragmentation**: Schemes are scattered across hundreds of government portals with varying navigational structures.
- **Complex Eligibility Criteria**: Eligibility rules involve overlapping conditions: household income ceilings, academic courses, caste category quotas, gender, age, and state domicile.
- **Incomplete Procedural Guidance**: Many portals list scheme names without providing complete checklists of required documentation, official application links, or grievance redressal avenues.
- **Cognitive Barrier**: Citizens often do not know bureaucratic keywords (e.g., searching for "money for college" vs. "Post-Matric Financial Assistance for Underrepresented Domiciles").

---

## Solution

**JanSahayak** bridges this gap by providing an intuitive, profile-aware discovery engine:
1. Citizens describe their need in plain English (e.g., *"I need a scholarship for my BTech"*).
2. They provide basic contextual profile attributes (age, education level, current course, household income, state, caste category, and disability status).
3. The serverless backend executes multi-attribute eligibility filtering and query ranking against a curated knowledge base of **1,005 verified government schemes** stored in Amazon S3.
4. Citizens receive actionable, structured scheme cards complete with step-by-step application instructions, required document checklists, official URLs, and verification timestamps.

---

## Features

- **Natural-Language Query Understanding**: Translates everyday requests into relevant benefit categories.
- **8-Factor Profile-Aware Eligibility Filtering**:
  - Educational level (Class 10, Class 12, Diploma, Undergraduate, Postgraduate, Ph.D.)
  - Specific degree/course discipline (Engineering / BTech, Medicine / MBBS, Science, Arts, Commerce, ITI)
  - Annual household income thresholds (e.g., <= ₹2.5 Lakh, ₹8 Lakh)
  - State / Union Territory domicile matching (Central vs. State-specific)
  - Caste / Social Category alignment (General, OBC, SC, ST, EWS)
  - Gender & Disability status (PwD) accommodations
  - Age boundaries
- **Comprehensive Scheme Intelligence**: Displays description, quantifiable financial benefits, exclusion clauses, mandatory document checklists, direct application links, and last verified dates.
- **Automated Ingestion Pipeline**: Modular Python pipeline (`ingestion/`) with schema validation and automated test suite (`tests/`) to process and normalize open government data.
- **High Performance & Resilience**: Sub-second serverless response times on AWS with graceful degradation when AI inference quotas are restricted.

---

## Architecture

```text
               +-------------------------------------------+
               |         Citizen (Web Browser)             |
               +-------------------------------------------+
                                     │
                                     │ HTTPS (POST /search)
                                     ▼
               +-------------------------------------------+
               |        Amazon API Gateway (HTTP API)      |
               |          Endpoint: us-east-1              |
               +-------------------------------------------+
                                     │
                                     │ Payload Proxy (v2.0)
                                     ▼
               +-------------------------------------------+
               |             AWS Lambda (Python)           |
               |       Execution & Eligibility Engine      |
               +-------------------------------------------+
                        │                          │
           boto3.get_object()                      │ Converse API
                        │                          │ (Planned Extension)
                        ▼                          ▼
       +-------------------------------+   +-------------------------------+
       |           Amazon S3           |   |        Amazon Bedrock         |
       |  Bucket: jansahayak-knowledge |   | Model: nova-2-lite-v1:0       |
       |     Object: schemes.json      |   | [Fallback Active: Quota = 0]  |
       |    (1,005 verified schemes)   |   +-------------------------------+
       +-------------------------------+                   │
                        │                                  │
                        └──────────────────┬───────────────┘
                                           ▼
                      +-----------------------------------------+
                      |         JSON Search Results             |
                      |   - Filtered Scheme Cards               |
                      |   - Required Documents & Links          |
                      |   - bedrock_available: false (fallback) |
                      +-----------------------------------------+
```

---

## AWS Services

| AWS Service | Role in JanSahayak | Configuration Details |
|-------------|-------------------|-----------------------|
| **Amazon API Gateway** | Managed HTTP API entry point | Public `POST /search` route, proxy integration to AWS Lambda, CORS enabled. |
| **AWS Lambda** | Serverless computational backend | Python runtime, event body parsing, multi-factor eligibility logic, S3 retrieval, sub-second latency. |
| **Amazon S3** | Durable, decoupled knowledge base | Bucket `jansahayak-knowledge-406658520064`, stores `schemes.json` (1,005 schemes, 4.1 MB). |
| **Amazon Bedrock** | GenAI reasoning layer *(Implemented)* | Converse API integration for `global.amazon.nova-2-lite-v1:0`; graceful fallback when account quota is 0. |
| **AWS IAM** | Security and role management | Principle of least privilege: S3 read access + Bedrock invocation + CloudWatch logging policies. |

---

## How It Works

1. **User Interaction**: The user enters a natural request (e.g. *"scholarship for higher education"*) and fills in optional profile filters in the UI.
2. **Request Dispatch**: The React application dispatches a JSON `POST` request to Amazon API Gateway.
3. **Lambda Execution**:
   - Lambda reads and parses `event["body"]`.
   - Fetches the active scheme catalog (`schemes.json`) from Amazon S3.
   - Evaluates eligibility criteria against user profile parameters (income limits, educational level, course restrictions, state domicile, and social category).
   - Computes query relevance scores and sorts matching schemes.
4. **Bedrock Attempt & Fallback**:
   - Lambda attempts to invoke Bedrock via the Converse API for personalized synthesis.
   - Catches account quota restriction (`ValidationException`), flags `bedrock_available: false`, and preserves the deterministic results.
5. **UI Presentation**: The frontend renders clean, interactive scheme cards with full details, document lists, and external portal links.

---

## API

### Search Schemes

- **Endpoint**: `POST https://ddf6zddofk.execute-api.us-east-1.amazonaws.com/search`
- **Headers**: `Content-Type: application/json`

#### Request Payload
```json
{
  "query": "scholarship for BTech",
  "profile": {
    "age": 20,
    "education": "Undergraduate",
    "education_level": "Undergraduate",
    "course": "BTech",
    "income": 200000,
    "state": "National",
    "category": "General",
    "disability": false
  }
}
```

#### Response Payload (Sample)
```json
{
  "schemes": [
    {
      "id": "edu-001",
      "name": "Central Sector Scheme of Scholarship for College and University Students",
      "ministry": "Ministry of Education",
      "level": "Central",
      "category": "Education",
      "state": "National",
      "description": "Financial assistance to meritorious students from low-income families...",
      "benefits": "₹12,000 per annum for Graduation; ₹20,000 per annum for Post-Graduation.",
      "eligibility": "Above 80th percentile in Class 12, regular course, family income < ₹4.5 Lakh.",
      "required_documents": [
        "Class 12 Marksheet",
        "Income Certificate",
        "Aadhaar Card",
        "Bank Account Details"
      ],
      "application_process": "Apply online through the National Scholarship Portal (NSP).",
      "official_url": "https://scholarships.gov.in",
      "last_verified": "2026-03-01"
    }
  ],
  "count": 1,
  "bedrock_available": false
}
```

#### Test via `curl`
```bash
curl -X POST https://ddf6zddofk.execute-api.us-east-1.amazonaws.com/search \
  -H "Content-Type: application/json" \
  -d '{"query": "scholarship", "profile": {"education": "Undergraduate", "income": 200000}}'
```

---

## Local Setup

### Prerequisites
- Node.js (v18+) & npm
- Python (v3.10+)
- AWS CLI configured (optional, for pipeline S3 upload)

### 1. Clone Repository
```bash
git clone https://github.com/saitejapcv/janSahayak.git
cd janSahayak
```

### 2. Frontend Setup
```bash
npm install
npm run dev
```
Open `http://localhost:5173` in your browser. The Vite dev server proxies `/api` directly to the live AWS API Gateway endpoint.

### 3. Ingestion Pipeline & Tests
```bash
# Run unit tests
python3 -m unittest discover -s tests

# Or with pytest
pytest tests/ -v
```

---

## Deployment

### Frontend (Static Web Hosting)
The frontend is built as a static Single Page Application:
```bash
npm run build
```
The output in `dist/` can be deployed to Amazon S3 static website hosting configured with Amazon CloudFront for global CDN distribution.

### Backend (AWS Lambda & API Gateway)
1. Package Lambda function:
   ```bash
   cd lambda/
   zip -r function.zip index.py
   ```
2. Upload to AWS Lambda via AWS Console or AWS CLI:
   ```bash
   aws lambda update-function-code \
     --function-name JanSahayakSearch \
     --zip-file fileb://function.zip \
     --region us-east-1
   ```

---

## Data

The scheme dataset is structured under a rigorous schema:
```json
{
  "id": "string",
  "name": "string",
  "category": "Education | Health | Agriculture | ...",
  "level": "Central | State",
  "state": "National | State Name",
  "ministry": "string",
  "description": "string",
  "benefits": "string",
  "eligibility": "string",
  "exclusions": "string",
  "required_documents": ["string"],
  "application_process": "string",
  "grievance_process": "string",
  "official_url": "string",
  "source_url": "string",
  "last_verified": "YYYY-MM-DD"
}
```

### Automated Ingestion Pipeline
The `ingestion/` directory contains:
- `ingest.py`: Fetches and normalizes raw government data from official sources.
- `transform.py`: Enforces schema conformance, strips HTML, and maps attributes.
- `upload_to_s3.py`: Validates payloads and syncs with `s3://jansahayak-knowledge-406658520064/schemes.json`.

---

## Bedrock Status

### Transparent Engineering Reality
Amazon Bedrock was architected into the system to synthesize natural-language eligibility summaries using the **Converse API** and the `global.amazon.nova-2-lite-v1:0` foundation model.

During hackathon testing in `us-east-1`, invocation resulted in:
```text
ValidationException: Operation not allowed
```
The AWS account had default on-demand inference quotas set to 0 for this model endpoint. Service quota requests were formally submitted, but remained in pending review.

### Graceful Fallback in Production
Rather than letting the application crash:
1. Lambda catches the exception safely.
2. The API returns `bedrock_available: false`.
3. Deterministic profile-aware filtering and relevance scoring continue to execute flawlessly.
4. The frontend renders an informative status badge while displaying complete, accurate scheme results.

---

## What I Learned

1. **API Gateway Event Structure**: Discovered that API Gateway HTTP API v2.0 passes incoming payloads as a raw string under `event["body"]`, requiring explicit deserialization via `json.loads()`.
2. **Serverless Memory & Payload Optimization**: Tested a 20 MB dataset (4,692 schemes) which caused Lambda cold-start memory spikes. Optimized knowledge base to 1,005 high-quality records (~4.1 MB) to achieve sub-second execution.
3. **IAM Least Privilege**: Replaced permissive wildcard policies with tight, resource-specific IAM roles for S3 read access and CloudWatch log streaming.
4. **Resilient System Design**: Engineered graceful fallbacks for third-party and AI cloud services when quotas or rate limits are encountered.

*For full engineering retrospective, read [WHAT_I_LEARNED.md](file:///Users/p.c.vsaiteja/janSahayak/docs/WHAT_I_LEARNED.md).*

---

## Challenges

| Challenge | Root Cause | Solution |
|-----------|------------|----------|
| **Empty Search Results** | `event["body"]` arrived as stringified JSON in Lambda. | Parsed `event.get("body")` safely with type checking. |
| **Browser CORS in Dev** | Direct API Gateway requests blocked by browser preflight (`OPTIONS`). | Configured Vite dev proxy and added CORS headers to Lambda responses. |
| **Bedrock Quota Lockout** | Account had 0 on-demand quota (`ValidationException`). | Built graceful degradation returning `bedrock_available: false` while serving deterministic results. |
| **Dataset Scaling vs Lambda Limits** | 20 MB raw JSON payload caused cold-start latency. | Normalized and filtered to 1,005 high-priority validated schemes (4.1 MB). |

---

## Future Roadmap

- [ ] **Multi-Lingual Support**: Add local Indian languages (Hindi, Telugu, Tamil, Marathi) for conversational discovery.
- [ ] **Bedrock Knowledge Bases (RAG)**: Migrate S3 JSON dataset into Amazon Bedrock Knowledge Bases with OpenSearch Serverless for hybrid vector search.
- [ ] **WhatsApp & SMS Bot**: Connect AWS Lex and Amazon SNS/Pinpoint for conversational discovery via messaging.
- [ ] **Direct Application Autofill**: Generate pre-filled scheme application forms using citizen profile attributes.

---

## Demo

- **Demo Video Script**: Detailed 3-minute narration script in [DEMO_SCRIPT.md](file:///Users/p.c.vsaiteja/janSahayak/docs/DEMO_SCRIPT.md).
- **Submission Writeup**: Comprehensive hackathon submission document in [HACKATHON_SUBMISSION.md](file:///Users/p.c.vsaiteja/janSahayak/docs/HACKATHON_SUBMISSION.md).
- **Live API Endpoint**: `POST https://ddf6zddofk.execute-api.us-east-1.amazonaws.com/search`

---

## Final Submission Checklist

- [x] Public GitHub repository
- [x] Clean, comprehensive README
- [x] Working live API Gateway endpoint
- [x] 3-minute video demo script prepared
- [x] Problem clearly explained
- [x] Working solution demonstrated
- [x] AWS architecture visualized and explained
- [x] Honest explanation of Bedrock status & fallback
- [x] AI coding tools documented (Google Antigravity)
- [x] Zero credentials or secret keys in repository
- [x] Automated tests passing

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.