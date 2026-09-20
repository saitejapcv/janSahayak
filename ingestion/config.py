"""
Configuration settings for JanSahayak Scheme Ingestion Pipeline.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# Root directory of the repository
BASE_DIR = Path(__file__).resolve().parent.parent

# Data paths
DATA_DIR = BASE_DIR / "data"
SCHEMES_FILE = DATA_DIR / "schemes.json"
BACKUP_DIR = DATA_DIR / "backups"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

# Data source configurations
# Permitted open dataset under CC BY 4.0 hosted on Hugging Face (derived from myScheme.gov.in)
DEFAULT_SOURCE_URL = "https://huggingface.co/datasets/smartduketech/indian-government-schemes-2025/resolve/main/Schemes.csv"
SCHEME_SOURCE_URL = os.getenv("SCHEME_SOURCE_URL", DEFAULT_SOURCE_URL)
SCHEME_API_KEY = os.getenv("SCHEME_API_KEY", "")

# S3 Configuration
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "jansahayak-knowledge-406658520064")
S3_OBJECT_KEY = os.getenv("S3_OBJECT_KEY", "schemes.json")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

# Networking
REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "45"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

# Canonical Category Vocabulary (Mandatory mapping)
VALID_CATEGORIES = [
    "Education",
    "Agriculture",
    "Healthcare",
    "Employment",
    "Housing",
    "Women & Child",
    "Disability",
    "Senior Citizens",
    "Financial Assistance",
    "Entrepreneurship",
    "Social Welfare",
    "Other"
]

# Canonical State names
CANONICAL_STATES = [
    "All India",
    "Andhra Pradesh",
    "Arunachal Pradesh",
    "Assam",
    "Bihar",
    "Chhattisgarh",
    "Goa",
    "Gujarat",
    "Haryana",
    "Himachal Pradesh",
    "Jharkhand",
    "Karnataka",
    "Kerala",
    "Madhya Pradesh",
    "Maharashtra",
    "Manipur",
    "Meghalaya",
    "Mizoram",
    "Nagaland",
    "Odisha",
    "Punjab",
    "Rajasthan",
    "Sikkim",
    "Tamil Nadu",
    "Telangana",
    "Tripura",
    "Uttar Pradesh",
    "Uttarakhand",
    "West Bengal",
    "Andaman and Nicobar Islands",
    "Chandigarh",
    "Dadra and Nagar Haveli and Daman and Diu",
    "Delhi",
    "Jammu and Kashmir",
    "Ladakh",
    "Lakshadweep",
    "Puducherry"
]
