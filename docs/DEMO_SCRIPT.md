# JanSahayak — 3-Minute Video Demo Script

**Hackathon**: WeMakeDevs AWS First Commit Hackathon  
**Target Duration**: 3 minutes (180 seconds)  
**Presenter**: Solo / Team Member  

---

## 🎬 Production & Recording Checklist

- [ ] Web application running at `http://localhost:5173` (or deployed URL).
- [ ] AWS Console open in a background tab showing:
  - Amazon API Gateway (Route `POST /search`).
  - AWS Lambda function console.
  - Amazon S3 bucket (`jansahayak-knowledge-406658520064`) showing `schemes.json`.
- [ ] Screen recorder set to 1080p, crisp audio with no background noise.

---

## ⏱️ Video Script Breakdown

### 0:00 – 0:20 | The Problem
**[Visual: Screen displays messy government portals, PDF notifications, and varied state scheme websites.]**

**Spoken (Voiceover)**:  
> "Across India, the central and state governments run thousands of welfare programs and scholarships to empower citizens. But for a typical student, farmer, or daily-wage worker, discovering which schemes they actually qualify for is overwhelming. Information is buried in complex gazette PDFs, scattered across hundreds of departmental portals, and written in dense bureaucratic jargon. Millions of eligible citizens miss life-changing benefits simply because they didn't know they qualified."

---

### 0:20 – 0:40 | Introducing JanSahayak
**[Visual: Transition cleanly to JanSahayak landing page at `http://localhost:5173`. Show the clean, trustworthy Indian civic-tech UI with the tagline "Government Benefits, Simplified.".]**

**Spoken**:  
> "To solve this, we built **JanSahayak**—a serverless government benefits navigator designed specifically for Indian citizens. JanSahayak allows any citizen to describe what they need in plain words, provide basic demographic details like their age, course, state, and family income, and instantly receive verified schemes with clear requirements and direct application links."

---

### 0:40 – 1:20 | Real User Query & Profile Input
**[Visual: Click into the search bar. Highlight the "Demo Preset (BTech Student)" button and click it to demonstrate instantaneous auto-filling of the query and 8 eligibility filters.]**

**Spoken**:  
> "Let's test a real-world scenario. Meet Saiteja, a 19-year-old student pursuing a BTech in Computer Science in Tamil Nadu, with an annual family income of ₹3 Lakhs. 
> 
> In the search bar, we enter: *'I need a scholarship for my BTech'*. 
> Under the Personal Eligibility Profile accordion, we specify:
> - Age: 19
> - Degree: BTech
> - Level: Undergraduate
> - Course: Computer Science
> - Annual Family Income: ₹3,00,000
> - State: Tamil Nadu
> - Category: General
> - Disability Status: No
>
> Now, we click **Find Schemes**."

---

### 1:20 – 2:00 | Live API Execution & Results
**[Visual: The search button animates with a spinner. The results smoothly transition with Motion animations. Result badge displays '1 scheme found' and renders the card for EDU004 — PM-USP Central Sector Scheme of Scholarship.]**

**Spoken**:  
> "Instantly, JanSahayak queries our live AWS backend. Notice how smart the profile filtering is: 
> We have other scholarships in our knowledge base, like the National Talent Scholarship (`EDU001`), but because `EDU001` is strictly reserved for Agriculture students, JanSahayak automatically excluded it!
> 
> Instead, it surfaces **EDU004: The Pradhan Mantri Uchchatar Shiksha Protsahan (PM-USP) Central Sector Scheme of Scholarship for College and University Students**. 
> Right on the card, Saiteja can scan key highlights: up to ₹20,000 annual assistance, regular degree course requirement, and the ₹4.5 Lakh income ceiling."

---

### 2:00 – 2:30 | Scheme Details & Official Application Portal
**[Visual: Click 'View details →'. The spring-animated side drawer slides open smoothly from the right.]**

**Spoken**:  
> "When the citizen clicks 'View details', an interactive drawer opens with verified, actionable guidance:
> 1. **About the Scheme**: What the scholarship does.
> 2. **Benefits & Assistance**: Number of fresh scholarships and coverage.
> 3. **Eligibility Checklist**: Percentile cut-offs, attendance rules, and Aadhaar bank linking.
> 4. **Required Documents**: 12th mark sheet, income certificate, and caste certificate.
> 5. **Application Process**: Clear step-by-step instructions for the National Scholarship Portal.
>
> Best of all, right at the top, there's a direct button: **'Apply / Visit Official Portal'**, taking the student straight to `scholarships.gov.in` to apply."

---

### 2:30 – 2:50 | AWS Serverless Architecture
**[Visual: Switch tab to AWS Console or architectural slide: showing API Gateway route `POST /search`, Lambda function, and S3 bucket `jansahayak-knowledge-406658520064`.]**

**Spoken**:  
> "Behind the scenes, JanSahayak is completely serverless on AWS:
> 1. Our React and Vite frontend makes an HTTP POST request to **Amazon API Gateway** in `us-east-1`.
> 2. API Gateway invokes an **AWS Lambda** function.
> 3. The Lambda function pulls our knowledge base directly from an **Amazon S3** bucket—which we scaled from 5 seed schemes to over **1,000 verified schemes** using an automated Python ingestion pipeline.
> 4. Lambda executes deterministic profile filtering and returns structured JSON in milliseconds."

---

### 2:50 – 3:00 | Honest Bedrock Status & Graceful Fallback
**[Visual: Highlight 'JanSahayak's Guidance' card on the UI displaying clean informational copy.]**

**Spoken**:  
> "We also implemented AI reasoning with **Amazon Bedrock** using the Converse API. Because our AWS account had zero inference quota during the hackathon, we built a resilient fallback: when Bedrock is unavailable, the API sets `bedrock_available: false` and the application continues working flawlessly using deterministic filtering. 
> 
> JanSahayak proves how AWS serverless tech can make government welfare accessible to every Indian citizen. Thank you!"

---

## 💡 Quick Tips for the Recording

1. **Pacing**: Speak at an energetic, confident, conversational speed (around 130–140 words per minute).
2. **Tab Pre-loading**: Have your browser tabs open ahead of time so transitions take less than 1 second.
3. **Cursor Movement**: Move your mouse deliberately; avoid shaking or clicking randomly.
4. **Resolution**: Keep your browser zoom at 100% or 110% so all UI elements and badges are crisp and legible.
