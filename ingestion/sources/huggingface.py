"""
Hugging Face Open Dataset Source Adapter for JanSahayak.
Fetches the CC BY 4.0 structured dataset of 4,600+ Indian schemes.
"""

import csv
import io
import logging
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

import requests

from .base import SchemeSource
from ..config import (
    SCHEME_SOURCE_URL,
    REQUEST_TIMEOUT_SECONDS,
    MAX_RETRIES,
    DATA_DIR,
)

logger = logging.getLogger(__name__)


class HuggingFaceCSVSource(SchemeSource):
    """
    Source adapter for the CC BY 4.0 open dataset hosted on Hugging Face:
    smartduketech/indian-government-schemes-2025 (Schemes.csv).
    """

    def __init__(self, source_url: Optional[str] = None, use_cache: bool = True):
        self.source_url = source_url or SCHEME_SOURCE_URL
        self.use_cache = use_cache
        self.cache_dir = DATA_DIR / ".cache"
        self.cache_file = self.cache_dir / "schemes_source_cache.csv"

    def get_source_name(self) -> str:
        return "smartduketech/indian-government-schemes-2025 (CC BY 4.0)"

    def fetch_schemes(self) -> List[Dict[str, Any]]:
        """
        Fetches schemes from the configured source URL or cache.
        
        Returns:
            List[Dict[str, Any]]: Raw rows as dictionaries.
        """
        # 1. Check if local path was specified
        local_path = Path(self.source_url)
        if local_path.is_file():
            logger.info(f"Loading schemes from local file: {local_path}")
            return self._parse_csv_file(local_path)

        # 2. Check if cached copy exists and caching is enabled
        if self.use_cache and self.cache_file.exists() and self.cache_file.stat().st_size > 1000:
            logger.info(f"Loading schemes from local cache: {self.cache_file}")
            return self._parse_csv_file(self.cache_file)

        # 3. Download from remote URL with retries
        logger.info(f"Downloading schemes dataset from: {self.source_url}")
        csv_content = self._download_with_retry()

        # Save to cache
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, "w", encoding="utf-8") as f:
                f.write(csv_content)
            logger.info(f"Cached raw dataset to: {self.cache_file}")
        except Exception as e:
            logger.warning(f"Could not write cache file: {e}")

        # Parse in-memory CSV
        reader = csv.DictReader(io.StringIO(csv_content))
        rows = [dict(row) for row in reader]
        logger.info(f"Successfully parsed {len(rows)} raw scheme records from CSV.")
        return rows

    def _parse_csv_file(self, filepath: Path) -> List[Dict[str, Any]]:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            rows = [dict(row) for row in reader]
        logger.info(f"Parsed {len(rows)} raw scheme records from {filepath.name}")
        return rows

    def _download_with_retry(self) -> str:
        last_exception = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                logger.info(f"HTTP GET {self.source_url} (Attempt {attempt}/{MAX_RETRIES})...")
                response = requests.get(
                    self.source_url,
                    timeout=REQUEST_TIMEOUT_SECONDS,
                    headers={"User-Agent": "JanSahayak-Ingestion-Pipeline/1.0"}
                )
                response.raise_for_status()
                return response.text
            except Exception as e:
                last_exception = e
                logger.warning(f"Attempt {attempt} failed: {e}")
                if attempt < MAX_RETRIES:
                    time.sleep(2 * attempt)

        raise RuntimeError(
            f"Failed to fetch scheme dataset from {self.source_url} after {MAX_RETRIES} attempts: {last_exception}"
        )
