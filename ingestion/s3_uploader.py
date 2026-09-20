"""
AWS S3 Uploader for JanSahayak Scheme Ingestion.
Uploads validated schemes.json to the target knowledge S3 bucket.
"""

import logging
from pathlib import Path
from typing import Optional

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from .config import S3_BUCKET_NAME, S3_OBJECT_KEY, AWS_REGION

logger = logging.getLogger(__name__)


def upload_schemes_to_s3(
    file_path: Path,
    bucket_name: Optional[str] = None,
    object_key: Optional[str] = None,
    region_name: Optional[str] = None,
) -> bool:
    """
    Uploads the specified JSON dataset to AWS S3 using ambient credentials.
    
    Args:
        file_path (Path): Local path to the file to upload.
        bucket_name (str, optional): Destination bucket name.
        object_key (str, optional): Destination object key in S3.
        region_name (str, optional): AWS region.
        
    Returns:
        bool: True if upload succeeded, False otherwise.
    """
    target_bucket = bucket_name or S3_BUCKET_NAME
    target_key = object_key or S3_OBJECT_KEY
    target_region = region_name or AWS_REGION

    if not file_path.exists():
        logger.error(f"Cannot upload non-existent file: {file_path}")
        return False

    file_size_kb = file_path.stat().st_size / 1024
    logger.info(f"Initiating S3 upload: {file_path} ({file_size_kb:.1f} KB) -> s3://{target_bucket}/{target_key}")

    try:
        s3_client = boto3.client("s3", region_name=target_region)
        s3_client.upload_file(
            Filename=str(file_path),
            Bucket=target_bucket,
            Key=target_key,
            ExtraArgs={
                "ContentType": "application/json; charset=utf-8",
            }
        )
        logger.info(f"Successfully uploaded dataset to s3://{target_bucket}/{target_key}")
        return True
    except (BotoCoreError, ClientError) as e:
        logger.error(f"Failed to upload to S3 (s3://{target_bucket}/{target_key}): {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during S3 upload: {e}")
        return False
