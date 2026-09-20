# What I Learned Building JanSahayak
### WeMakeDevs AWS First Commit Hackathon Engineering Retrospective

Building **JanSahayak** as a first-time serverless project on Amazon Web Services (AWS) provided deep, hands-on exposure to cloud architecture, distributed debugging, serverless constraints, and AI service integration.

Rather than high-level generalities, this document details the specific technical lessons, architecture insights, and debugging breakthroughs discovered while taking JanSahayak from an initial local concept to a live cloud application.

---

## 1. AWS Cloud Architecture: Connecting the Serverless Chain

The core architecture follows a decoupled, stateless pattern:

```text
React / Vite Web Client (Browser)
       │
       ▼  HTTPS POST /search
Amazon API Gateway (HTTP API)
       │
       ▼  Payload Proxy Integration (v2.0)
AWS Lambda (Python 3.x Execution Runtime)
       │
       ▼  boto3.client('s3').get_object()
Amazon S3 (Knowledge Base Bucket: schemes.json)
       │
       ▼  Profile-Aware Filtering & Scoring
Matching Scheme Results (JSON Payload)
```

### Key Architectural Takeaways
- **True Decoupling**: Storing scheme data inside Amazon S3 rather than baking it into the Lambda deployment package or a frontend bundle ensures that datasets can be updated or expanded without rebuilding the client or redeploying Lambda code.
- **Stateless Execution**: The Lambda function retains no session state between invocations; every incoming request contains both the user query and the profile attributes required for deterministic evaluation.
- **Single Responsibility**: API Gateway handles route resolution and basic protocol validation; Lambda executes business logic and scheme matching; S3 guarantees durable object storage.

---

## 2. AWS Lambda: Handlers, Event Payloads, and Runtime Constraints

### The Event Payload Trap (`event.body` String vs Object)
When transitioning from local Python testing to AWS Lambda triggered by API Gateway HTTP APIs, the first major issue was payload parsing. 

In local script testing, incoming test payloads are typically standard Python dictionaries (`{"query": "scholarship", "profile": {...}}`). However, API Gateway's Payload Format Version 2.0 passes the HTTP body as a raw serialized string:
```python
# What fails:
query = event.get("query", "")  # Returns None!

# What works:
import json

raw_body = event.get("body", "{}")
if isinstance(raw_body, str):
    body = json.loads(raw_body)
else:
    body = raw_body or {}

query = body.get("query", "")
profile = body.get("profile", {})
```
Failing to parse `event["body"]` caused the Lambda function to see empty queries on every invocation, returning zero matches despite valid frontend inputs.

### Memory Allocation vs Ingestion Scale
During our scaling tests, we generated a comprehensive dataset of 4,692 schemes (~20 MB JSON). When uploaded to S3, the default Lambda memory allocation (128 MB) caused execution timeouts and memory exhaustion (`MemoryError` / task timed out after 3.00 seconds) while fetching and parsing the entire JSON object into memory on cold starts.

**Solution & Takeaway**:
We scaled the dataset to 1,005 high-priority, fully validated schemes (~4.1 MB JSON). This allowed the Lambda execution runtime to fetch, parse, and score records within 400–800 ms while remaining well within standard memory limits. For scaling beyond 10,000 schemes, an indexed datastore (Amazon DynamoDB or OpenSearch) is the proper architectural evolution.

---

## 3. Amazon API Gateway: HTTP APIs, Routes, and CORS

### Route Definition & Integration
- Configured an **HTTP API** (which offers lower latency and lower cost compared to REST APIs) with a dedicated `POST /search` route.
- Created an AWS Lambda proxy integration so that requests are passed directly into the function handler.

### Cross-Origin Resource Sharing (CORS) in Development vs Production
In a web application where the frontend runs locally (`http://localhost:5173`) or on a separate domain from the API Gateway endpoint (`https://ddf6zddofk.execute-api.us-east-1.amazonaws.com`), browser preflight `OPTIONS` requests fail unless CORS headers are handled properly:

1. **Lambda Response Headers**: The Lambda response must explicitly return CORS headers:
   ```python
   return {
       "statusCode": 200,
       "headers": {
           "Content-Type": "application/json",
           "Access-Control-Allow-Origin": "*",
           "Access-Control-Allow-Headers": "Content-Type,Authorization",
           "Access-Control-Allow-Methods": "OPTIONS,POST"
       },
       "body": json.dumps(response_payload)
   }
   ```
2. **Frontend Dev Proxy**: In Vite, configuring a local server proxy (`/api -> https://ddf6zddofk...`) eliminates browser preflight restrictions during rapid development cycles.

---

## 4. Amazon S3: Managing Structured Scheme Knowledge

### Bucket Organization & Retrieval
- S3 Bucket: `jansahayak-knowledge-406658520064`
- Object: `schemes.json`
- Rather than maintaining database connection pools for read-heavy, low-frequency write data, S3 provides 99.999999999% (11 9's) durability with minimal operational overhead.

### Data Fetching with `boto3`
```python
s3_client = boto3.client('s3', region_name='us-east-1')

def fetch_schemes_from_s3(bucket: str, key: str):
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        data = response['Body'].read().decode('utf-8')
        return json.loads(data)
    except Exception as e:
        print(f"Error fetching from S3: {str(e)}")
        return []
```
This pattern allows automated data pipelines to upload refreshed scheme catalogs directly to S3 without interrupting running Lambda instances.

---

## 5. AWS IAM: Least Privilege & Execution Roles

Working with AWS Identity and Access Management (IAM) highlighted the necessity of scoping permissions specifically rather than relying on wildcard access (`*`):

1. **Lambda Basic Execution Role**: `AWSLambdaBasicExecutionRole` enables CloudWatch Logs ingestion (`logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents`). Without this, debugging silent failures in Lambda is virtually impossible.
2. **S3 Read-Only Access**: Scoped exclusively to the specific bucket ARN:
   ```json
   {
       "Effect": "Allow",
       "Action": ["s3:GetObject"],
       "Resource": "arn:aws:s3:::jansahayak-knowledge-406658520064/*"
   }
   ```
3. **Bedrock Invocation Policy**: Scoped specifically to the model resource:
   ```json
   {
       "Effect": "Allow",
       "Action": ["bedrock:InvokeModel"],
       "Resource": "arn:aws:bedrock:us-east-1::foundation-model/global.amazon.nova-2-lite-v1:0"
   }
   ```
Understanding the separation of concerns between user credentials, role assumption, and service trust policies was a major milestone in understanding AWS cloud security.

---

## 6. Amazon Bedrock: Integration, Quotas, and Graceful Fallback

### Integration via the Converse API
The Lambda function was designed to leverage Amazon Bedrock via the modern `converse` API for natural-language reasoning and personalized eligibility explanations:

```python
bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')

def invoke_bedrock_reasoning(query: str, profile: dict, matching_schemes: list):
    try:
        messages = [
            {
                "role": "user",
                "content": [{"text": construct_prompt(query, profile, matching_schemes)}]
            }
        ]
        response = bedrock_client.converse(
            modelId="global.amazon.nova-2-lite-v1:0",
            messages=messages,
            inferenceConfig={"temperature": 0.2, "maxTokens": 1000}
        )
        return response['output']['message']['content'][0]['text'], True
    except Exception as e:
        print(f"Bedrock invocation failed: {str(e)}")
        return None, False
```

### The Zero Inference Quota Reality & Error 400
During development in `us-east-1`, attempting to invoke `global.amazon.nova-2-lite-v1:0` consistently raised:
```text
ClientError: An error occurred (ValidationException) when calling the Converse operation: Operation not allowed
```
Investigation revealed that for new AWS accounts or specific model endpoints, the default provisioned/on-demand inference quota can be zero until explicitly approved via AWS Service Quotas. While quota increase requests were submitted, approval remained pending during the hackathon timeline.

### Engineering Graceful Degradation
Instead of letting the entire application crash when Bedrock fails, the Lambda was built with resilience as a first-class requirement:
1. The Bedrock call is isolated within a `try/except` block.
2. When the exception triggers, the API returns:
   ```json
   {
       "schemes": [...],
       "count": 4,
       "bedrock_available": false,
       "fallback_reason": "Bedrock inference quota not available in account. Deterministic filtering active."
   }
   ```
3. The React frontend checks `bedrock_available` and displays an informative status banner while seamlessly presenting the deterministic search results.

This ensures zero downtime for citizens looking for critical government assistance.

---

## 7. Real-World Debugging Lessons

| # | Bug Encountered | Root Cause | Solution |
|---|----------------|------------|----------|
| 1 | API returning 0 results for valid queries | `event["body"]` was arriving as a stringified JSON string from API Gateway, but code was querying `event.get("query")` directly. | Added `json.loads(event["body"])` with type validation. |
| 2 | Frontend failing to fetch live API in dev | Browser cross-origin preflight checks (`OPTIONS`) blocked requests from `localhost:5173`. | Added Vite dev proxy configuration and explicit Lambda CORS response headers. |
| 3 | Lambda 500 Internal Server Error on 20 MB dataset | Full dataset exceeded memory/execution timeout on cold starts. | Filtered dataset down to 1,005 valid schemes (4.1 MB) for sub-second retrieval. |
| 4 | Bedrock `ValidationException: Operation not allowed` | Account-level inference quotas were set to 0 by AWS default policy. | Built graceful fallback returning `bedrock_available: false` while keeping matching pipeline fully functional. |
| 5 | Regional Mismatch | S3 bucket created in `us-east-1` while an initial test client was configured with `ap-south-1`. | Standardized all AWS services and boto3 client instances to `us-east-1`. |

---

## 8. Frontend & Live API Integration

Connecting a React 19 / Vite frontend to a live AWS cloud backend provided important lessons in user experience design:
- **Optimistic vs Defensive UI**: When querying an external cloud backend, network latency can fluctuate. We implemented clear loading skeletons and subtle pulse indicators to communicate progress.
- **Dynamic Response Rendering**: The UI unpacks complex scheme fields (target beneficiaries, exclusion clauses, required documentation checklists, and application step-by-step guides) dynamically.
- **Empty-State Guidance**: When a user's profile disqualifies them from certain schemes (e.g., income over limit), the system displays helpful, actionable guidance explaining why no schemes matched and which filters might be relaxed.

---

## 9. Product Evolution: From Keyword Matching to Profile Navigation

The project underwent a significant conceptual evolution:

1. **Phase 1: Naive Keyword Search**: Initially, the system attempted to find schemes by matching query words ("scholarship", "farmer") directly against scheme titles. This produced many false positives and omitted schemes with differing nomenclature.
2. **Phase 2: Profile-Aware Multi-Factor Filtering**: We introduced structured citizen attributes (age, education level, course/discipline, household income, state, caste category, and disability status). A scheme is only returned if the user meets eligibility criteria.
3. **Phase 3: Actionable Citizen Intelligence**: We moved beyond merely displaying names of schemes to providing actionable guides: exact required documents, direct official URLs, grievance mechanisms, and verification timestamps.
4. **Phase 4: Automated Ingestion Architecture**: We designed an automated Python ingestion pipeline (`ingestion/ingest.py`) with schema validation and test coverage, preparing the system to scale from 1,005 schemes to tens of thousands.

---

## Summary

The WeMakeDevs AWS First Commit Hackathon was a practical masterclass in building real cloud applications. From navigating API Gateway request formats and IAM boundaries to engineering resilient fallbacks when AI services encounter quota barriers, the JanSahayak journey was grounded in real-world software engineering and resilient systems design.
