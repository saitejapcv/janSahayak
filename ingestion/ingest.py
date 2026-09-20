#!/usr/bin/env python3
"""
JanSahayak Automated Scheme Ingestion Pipeline CLI.

Usage:
  python ingestion/ingest.py [options]

Options:
  --dry-run             Fetch, normalize, and validate without uploading to S3 or overwriting production.
  --category <name>     Filter schemes by canonical category (e.g. Agriculture, Education).
  --state <name>        Filter schemes by state (e.g. "Tamil Nadu", "All India").
  --limit <number>      Process only the first N schemes (useful for quick testing).
  --source-url <url>    Override default dataset source URL or specify a local CSV path.
  --no-cache            Bypass local CSV cache and force fresh download from remote source.
  --verbose             Enable detailed debug logging.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from ingestion.config import SCHEMES_FILE, VALID_CATEGORIES, S3_BUCKET_NAME, S3_OBJECT_KEY
from ingestion.sources import HuggingFaceCSVSource
from ingestion.normalize import normalize_scheme
from ingestion.deduplicate import deduplicate_schemes
from ingestion.validate import validate_dataset
from ingestion.backup import create_backup
from ingestion.s3_uploader import upload_schemes_to_s3


def setup_logging(verbose: bool = False):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def load_existing_seed_schemes() -> List[Dict[str, Any]]:
    """Loads existing baseline schemes from data/seeds.json or data/schemes.json if present."""
    seeds_file = BASE_DIR / "data" / "seeds.json"
    target = seeds_file if seeds_file.exists() else SCHEMES_FILE
    if not target.exists():
        return []
    try:
        with open(target, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
    except Exception as e:
        logging.warning(f"Could not read existing seed schemes: {e}")
    return []


def run_pipeline(
    dry_run: bool = False,
    category_filter: str = None,
    state_filter: str = None,
    limit: int = None,
    source_url: str = None,
    no_cache: bool = False,
) -> bool:
    logger = logging.getLogger("ingestion.pipeline")
    logger.info("=" * 65)
    logger.info("🚀 Starting JanSahayak Scheme Ingestion Pipeline")
    logger.info(f"   Mode: {'DRY RUN (No S3 Upload)' if dry_run else 'PRODUCTION (Live Update & S3 Upload)'}")
    if category_filter:
        logger.info(f"   Category Filter: {category_filter}")
    if state_filter:
        logger.info(f"   State Filter: {state_filter}")
    if limit:
        logger.info(f"   Record Limit: {limit}")
    logger.info("=" * 65)

    # Step 1: Initialize Source Adapter and Fetch
    logger.info("\n--- Step 1: Fetching Data from Permitted Source ---")
    source = HuggingFaceCSVSource(source_url=source_url, use_cache=not no_cache)
    logger.info(f"Using source adapter: {source.get_source_name()}")

    try:
        raw_schemes = source.fetch_schemes()
    except Exception as e:
        logger.error(f"Failed to fetch data from source: {e}")
        return False

    total_fetched = len(raw_schemes)
    logger.info(f"Total raw records fetched: {total_fetched}")

    if limit and limit > 0:
        raw_schemes = raw_schemes[:limit]
        logger.info(f"Applied limit: processing {len(raw_schemes)} records.")

    # Step 2: Normalization
    logger.info("\n--- Step 2: Normalizing to JanSahayak Schema ---")
    normalized_incoming = []
    for raw in raw_schemes:
        try:
            norm = normalize_scheme(raw)
            # Apply category filter if specified
            if category_filter and norm["category"].lower() != category_filter.lower():
                continue
            # Apply state filter if specified
            if state_filter and state_filter.lower() not in norm["state"].lower():
                continue
            normalized_incoming.append(norm)
        except Exception as e:
            logger.warning(f"Error normalizing record {raw.get('name', 'Unknown')}: {e}")

    normalized_count = len(normalized_incoming)
    logger.info(f"Normalized records passing filters: {normalized_count}")

    # Step 3: Seed Preservation & Deduplication
    logger.info("\n--- Step 3: Merging Seed Records & Deduplicating ---")
    seed_records = load_existing_seed_schemes()
    logger.info(f"Loaded {len(seed_records)} existing seed schemes from {SCHEMES_FILE.name}")

    # Combine existing seeds first (so they retain priority), then incoming normalized
    combined_pool = seed_records + normalized_incoming
    unique_schemes, duplicates_count = deduplicate_schemes(combined_pool)
    logger.info(f"Deduplication complete. Duplicates removed: {duplicates_count}. Remaining: {len(unique_schemes)}")

    # Step 4: Validation
    logger.info("\n--- Step 4: Validating Scheme Conformance ---")
    valid_schemes, rejected_items = validate_dataset(unique_schemes)
    valid_count = len(valid_schemes)
    rejected_count = len(rejected_items)

    if rejected_items:
        logger.warning(f"Validation rejected {rejected_count} records. Sample rejection reasons:")
        for idx, (rec, reasons) in enumerate(rejected_items[:5]):
            rec_id = rec.get("id", "Unknown")
            rec_name = rec.get("name", "Unknown")[:40]
            logger.warning(f"  [{idx+1}] {rec_id} ({rec_name}...): {', '.join(reasons)}")

    # Print Ingestion Summary Report
    print("\n" + "=" * 55)
    print(" 📊 JANSAHAYAK SCHEME INGESTION REPORT")
    print("=" * 55)
    print(f" Total raw fetched       : {total_fetched}")
    print(f" Normalized              : {normalized_count}")
    print(f" Duplicates removed      : {duplicates_count}")
    print(f" Valid records approved  : {valid_count}")
    print(f" Rejected records        : {rejected_count}")
    print("=" * 55 + "\n")

    if valid_count == 0:
        logger.error("No valid scheme records produced. Ingestion aborted.")
        return False

    # Step 5: Output Generation & Backup
    if dry_run:
        dry_run_output = BASE_DIR / "data" / "schemes_dry_run.json"
        with open(dry_run_output, "w", encoding="utf-8") as f:
            json.dump(valid_schemes, f, indent=2, ensure_ascii=False)
        logger.info(f"DRY RUN SUCCESS: Written {valid_count} schemes to temporary file: {dry_run_output}")
        logger.info("No production files were modified, and S3 was not touched.")
        return True

    logger.info("\n--- Step 5: Creating Backup & Writing Production Dataset ---")
    backup_file = create_backup(SCHEMES_FILE)
    if backup_file:
        logger.info(f"Safeguard backup verified at: {backup_file}")

    # Write new schemes.json
    try:
        with open(SCHEMES_FILE, "w", encoding="utf-8") as f:
            json.dump(valid_schemes, f, indent=2, ensure_ascii=False)
        file_size_mb = SCHEMES_FILE.stat().st_size / (1024 * 1024)
        logger.info(f"Updated {SCHEMES_FILE} with {valid_count} schemes ({file_size_mb:.2f} MB).")
    except Exception as e:
        logger.error(f"Failed to write production schemes.json: {e}")
        return False

    # Step 6: S3 Upload
    logger.info("\n--- Step 6: Uploading to AWS S3 Knowledge Bucket ---")
    upload_success = upload_schemes_to_s3(
        file_path=SCHEMES_FILE,
        bucket_name=S3_BUCKET_NAME,
        object_key=S3_OBJECT_KEY
    )

    if upload_success:
        logger.info("=" * 65)
        logger.info("🎉 Ingestion Pipeline Completed Successfully!")
        logger.info(f"   S3 Location: s3://{S3_BUCKET_NAME}/{S3_OBJECT_KEY}")
        logger.info(f"   Total Schemes Ingested: {valid_count}")
        logger.info("=" * 65)
        return True
    else:
        logger.error("❌ S3 upload failed. Local data/schemes.json has been preserved.")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="JanSahayak Automated Scheme Ingestion Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run pipeline, validate, and write data/schemes_dry_run.json without updating production or S3.",
    )
    parser.add_argument(
        "--category",
        type=str,
        default=None,
        help="Filter schemes by canonical category (e.g. Agriculture, Education, Healthcare).",
    )
    parser.add_argument(
        "--state",
        type=str,
        default=None,
        help='Filter schemes by state (e.g. "Tamil Nadu", "All India").',
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of raw records processed (useful for rapid dry-runs).",
    )
    parser.add_argument(
        "--source-url",
        type=str,
        default=None,
        help="Override default dataset source URL or provide path to a local CSV file.",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Bypass local cache and download fresh dataset from source.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable detailed debug logs.",
    )

    args = parser.parse_args()
    setup_logging(verbose=args.verbose)

    success = run_pipeline(
        dry_run=args.dry_run,
        category_filter=args.category,
        state_filter=args.state,
        limit=args.limit,
        source_url=args.source_url,
        no_cache=args.no_cache,
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
