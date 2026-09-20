"""
Abstract Base Class for Scheme Data Sources.
Enables pluggable data source ingestion.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class SchemeSource(ABC):
    """Abstract class for scheme data providers."""

    @abstractmethod
    def fetch_schemes(self) -> List[Dict[str, Any]]:
        """
        Fetches raw scheme records from the source.
        
        Returns:
            List[Dict[str, Any]]: Raw records as dictionaries.
        """
        pass

    @abstractmethod
    def get_source_name(self) -> str:
        """Returns the canonical name or identifier of the source."""
        pass
