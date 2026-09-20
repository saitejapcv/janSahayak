# JanSahayak — Hackathon Submission

**WeMakeDevs AWS First Commit Hackathon**

---

### 1. Project Name
**JanSahayak** (जन सहायक — *"Citizen's Helper"*)  
*Tagline: Government Benefits, Simplified.*

---

### 2. One-Line Description
A serverless, profile-aware government benefits navigator that helps Indian citizens discover verified welfare schemes, understand eligibility criteria, and access official application portals through simple natural-language queries.

---

### 3. Problem
India has thousands of central and state government welfare schemes covering scholarships, agriculture, healthcare, housing, and social security. However, this information is fragmented across hundreds of disparate ministry websites, state portals, and PDF gazettes. 

Most citizens—especially students, rural farmers, and low-income families:
- Do not know which schemes they qualify for.
- Struggle to navigate bureaucratic jargon and complex eligibility conditions.
- Miss application deadlines or submit incomplete documents.
- Lack a single unified starting point tailored to their personal demographic profile.

---

### 4. Solution
JanSahayak simplifies citizen welfare discovery into a transparent 2-step experience:
1. **Express What You Need**: Citizens describe their situation in plain language (e.g., *"I need a scholarship for my BTech"* or *"farmer crop assistance"*).
2. **Refine With Demographics**: Users optionally provide basic profile details (age, education level, course, family income, state, category, disability).
3. **Actionable Results**: JanSahayak filters and ranks matching schemes, displays key benefit highlights and checklists, and directs citizens straight to the verified application portal (such as the National Scholarship Portal).

---

### 5. How It Works
1. The user inputs their need and demographic attributes into the React frontend.
2. The frontend sends a clean JSON payload via HTTP POST to Amazon API Gateway.
3. API Gateway routes the request to an AWS Lambda function.
4. The Lambda function loads the knowledge dataset (`schemes.json`) from Amazon S3.
5. The backend executes deterministic, multi-attribute eligibility filtering (comparing age limits, education level, stream, income thresholds, state domicile, and social category).
6. The backend attempts generative reasoning via Amazon Bedrock (Converse API); if Bedrock quota is unavailable, it activates a seamless fallback (`bedrock_available: false`).
7. The matched schemes and guidance are returned to the client and rendered in clean, scannable cards with a detailed slide-out drawer.

---

### 6. AWS Architecture

```text
[ Citizen / Web Browser ]
           │
           ▼
[ React + Vite Frontend (GSAP & Motion) ]
           │
           ▼  POST /search (JSON)
[ Amazon API Gateway (HTTP API - us-east-1) ]
           │
           ▼  Lambda Proxy Event
[ AWS Lambda Function ]
     │               │
     ▼ (Read Data)   ▼ (Inference / Fallback)
[ Amazon S3 ]   [ Amazon Bedrock ]
  Bucket:         Model: global.amazon.nova-2-lite-v1:0
  jansahayak-     Status: Fallback active (quota blocked)
  knowledge-      Graceful degradation: bedrock_available: false
  406658520064    
  Object:
  schemes.json
```

**AWS Services Used**:
- **Amazon S3**: Hosts the verified scheme knowledge base (`schemes.json`, 1,005+ schemes, ~4.1 MB) with high durability and fast in-region access.
- **AWS Lambda**: Executes serverless query parsing, S3 data retrieval, and deterministic eligibility filtering without persistent server management.
- **Amazon API Gateway**: Provides a public, managed HTTP API endpoint with low latency and seamless Lambda proxy integration.
- **Amazon Bedrock (Designed & Integrated)**: Implemented with the Converse API targeting `global.amazon.nova-2-lite-v1:0` for AI guidance, backed by an automated fallback.

---

### 7. Key Features
- **Natural Language Search**: Citizens find schemes by typing intuitive queries rather than knowing bureaucratic program titles.
- **Profile-Aware Eligibility Engine**: Filters schemes dynamically based on 8 citizen parameters:
  - Age
  - Education (Degree)
  - Education Level (School, Undergraduate, Postgraduate)
  - Course / Discipline (e.g., Computer Science vs. Agriculture)
  - Annual Family Income (with Indian Rupee `₹` threshold matching)
  - State / Union Territory (Central vs. State jurisdiction)
  - Social Category (General, OBC, SC, ST)
  - Disability Status (PwD)
- **Scannable Information Cards**: Displays key benefits, prerequisites, and last-verified timestamps at a glance.
- **Slide-Out Details Drawer**: Accessible slide-over panel on desktop and bottom sheet on mobile providing comprehensive information: About, Benefits, Eligibility checklist, Required Documents, and Step-by-step Application Process.
- **Direct Portal Links**: Directly links to authentic government portals (`official_url` such as `scholarships.gov.in`) and source records on `myScheme.gov.in`.
- **Demo Preset Button**: A one-click shortcut ("Demo Preset: BTech Student") allowing hackathon judges to evaluate the exact target flow instantly.
- **Fluid Micro-Animations**: Built with GSAP for staggered hero entrances and Motion for spring-animated drawers and card interactions.

---

### 8. What We Built
1. **Production-Ready Frontend**: Modern Indian civic-tech UI built with React 19, Vite 6, Lucide icons, GSAP, and Motion.
2. **Serverless Backend API**: Deployed on AWS API Gateway + Lambda + S3 handling search, filtering, and structured JSON responses.
3. **Automated Scheme Ingestion Pipeline** (`ingestion/`):
   - A modular Python ETL pipeline that fetches 4,600+ schemes from an open CC BY 4.0 dataset derived from official `myScheme.gov.in` records.
   - Normalizes categories into a 12-class canonical vocabulary and cleans state names.
   - Parses markdown/HTML into structured benefit and document lists.
   - Deduplicates and strictly validates every record.
   - Automatically creates timestamped backups in `data/backups/`.
   - Uploads validated datasets to `s3://jansahayak-knowledge-406658520064/schemes.json` via Boto3.
4. **Automated Unit Test Suite** (`tests/`): 14 passing tests in Pytest covering normalization, validation, list extraction, and S3 upload resilience.

---

### 9. Challenges and How We Solved Them
1. **API Gateway Event Structure**:
   - *Challenge*: Lambda initially received requests where `event.body` was a serialized string rather than a parsed dictionary, causing parsing errors.
   - *Solution*: Added robust JSON parsing of `event.body` with defensive fallback handling and clean HTTP error responses.
2. **Browser CORS Handling**:
   - *Challenge*: Direct browser requests to API Gateway were blocked by browser cross-origin security because preflight `OPTIONS` returned 404.
   - *Solution*: Configured Vite reverse proxy (`/api/*`) for local development and preview, and built resilient fallback logic in the frontend API client.
3. **Large Dataset Memory Constraints in Lambda**:
   - *Challenge*: Ingesting the full 4,692 schemes created a 20 MB JSON file that exceeded Lambda's default memory and cold-start timeout when parsing `json.loads()` on every invocation.
   - *Solution*: Tested dataset thresholds and stabilized production ingestion at 1,005 high-value schemes (4.1 MB), providing sub-second latency and 100% API reliability.
4. **Bedrock Inference Quota Lockout**:
   - *Challenge*: Amazon Bedrock model access returned `ValidationException: Operation not allowed` due to account inference quotas being set to 0.
   - *Solution*: Built an architectural circuit breaker: if Bedrock fails, the Lambda sets `bedrock_available: false` and delivers the matched schemes normally, while the frontend displays helpful guidance without confusing error banners.

---

### 10. What I Learned
- **Event-Driven Lambda Architecture**: Gained deep hands-on understanding of the API Gateway proxy event payload, header propagation, and returning structured API Gateway responses (`statusCode`, `headers`, `body`).
- **S3 as a Dynamic Knowledge Layer**: Discovered how decoupling knowledge datasets into S3 allows updating thousands of scheme records without modifying or redeploying backend Lambda code.
- **Graceful Degradation in AI Products**: Learned that production GenAI applications must never fail entirely when model inference is unavailable or rate-limited. Deterministic rule-based filtering must act as a reliable baseline.
- **Data Engineering for Public Welfare**: Learned how to normalize inconsistent, semi-structured public records (bullet points, HTML tags, varied currency formats) into a strict, validated schema.
- **Least-Privilege IAM Principles**: Understood the necessity of scoping IAM user and role policies specifically to necessary S3 bucket actions (`s3:PutObject`, `s3:GetObject`) rather than using administrative wildcards.

---

### 11. Amazon Bedrock Status & Engineering Decision
- **Implementation**: The backend code integrates with Amazon Bedrock using the Converse API targeting `global.amazon.nova-2-lite-v1:0`.
- **Limitation Encountered**: The AWS account utilized for this hackathon had its Bedrock model inference quotas set to 0 by default. Quota increase requests were submitted through AWS Service Quotas, but remained pending during development.
- **Engineering Decision**: Rather than halting development or faking AI output, we engineered a graceful fallback mechanism. When Bedrock returns `Operation not allowed`, the backend catches the exception, flags `bedrock_available: false`, and delivers the matched schemes filtered by deterministic rules. The application remains fully functional and ready to enable generative reasoning as soon as AWS activates quota access.

---

### 12. Future Improvements
- **Amazon OpenSearch / Kendra Integration**: Replace in-memory JSON scanning with Amazon OpenSearch Service for vector-based semantic retrieval across tens of thousands of schemes.
- **Multilingual Voice Interface**: Integrate Amazon Polly and Amazon Transcribe to allow rural citizens to query welfare benefits in regional Indian languages (Hindi, Tamil, Telugu, etc.) via voice.
- **Automated EventBridge Scheduling**: Deploy the ingestion script into an AWS ECS task or scheduled Lambda triggered weekly by Amazon EventBridge to automatically refresh scheme guidelines.
- **Document Eligibility Pre-Checker**: Allow users to upload certificate scans to S3 to verify income certificates or mark sheets against scheme criteria.

---

### 13. Tech Stack
- **Frontend**: React 19, Vite 6, GSAP 3, Motion (Framer Motion), Lucide React
- **Backend & Cloud**: AWS Lambda (Python 3.12 runtime), Amazon API Gateway (HTTP API), Amazon S3, Amazon Bedrock (Converse API, pending quota)
- **Data Pipeline**: Python 3, Requests, Boto3, Pytest, Python-Dotenv
- **Dataset**: `smartduketech/indian-government-schemes-2025` (CC BY 4.0), derived from `myScheme.gov.in`
- **AI Coding Tool Used**: Google Antigravity (Advanced Agentic AI Pair Programmer)

---

### 14. Demo Instructions
1. **Live Search**: Open the web application at `http://localhost:5173`.
2. **Demo Preset**: Click **"Demo Preset (BTech Student)"** to auto-fill the evaluation profile:
   - Query: `"I need a scholarship for my BTech"`
   - Age: `19` | Degree: `BTech` | Level: `Undergraduate` | Course: `Computer Science`
   - Family Income: `₹3,00,000` | State: `Tamil Nadu` | Category: `General` | Disability: `No`
3. **Execute Search**: Click **"Find Schemes"**.
4. **Observe Results**: Notice that **`EDU004` (PM-USP Central Sector Scholarship)** appears, while `EDU001` (Agriculture-specific) is excluded by profile filtering.
5. **View Scheme Details**: Click **"View details →"** on `EDU004` to explore benefits, eligibility rules, and click **"Apply / Visit Official Portal ↗"** (`scholarships.gov.in`).
6. **Farmer Search**: Clear the form, search `"farmer assistance"`, and explore newly ingested agriculture schemes across Indian states.
