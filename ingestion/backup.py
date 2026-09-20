"""
Backup utility for JanSahayak datasets.
Safeguards existing data before ingestion writes.
"""

import shutil
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from .config import SCHEMES_FILE, BACKUP_DIR

logger = logging.getLogger(__name__)


def create_backup(source_file: Optional[Path] = None) -> Optional[Path]:
    """
    Creates a timestamped backup of the current schemes file.
    
    Returns:
        Optional[Path]: Path to the backup file, or None if source did not exist.
    """
    target_source = source_file or SCHEMES_FILE
    if not target_source.exists():
        logger.info(f"No existing file to backup at {target_source}")
        return None

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"schemes_{timestamp}.json"

    shutil.copy2(target_source, backup_path)
    logger.info(f"Created local backup: {backup_path} ({backup_path.stat().st_size} bytes)")
    return backup_path
