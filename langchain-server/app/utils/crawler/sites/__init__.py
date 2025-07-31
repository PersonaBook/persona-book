from typing import Any, Dict, Optional
from app.utils.crawler.sites import w3schools, geeksforgeeks, oracle
from app.utils.crawler.sites.base import BaseCleaner

SITE_CLEANERS: Dict[str, Any] = {
    "w3schools.com": w3schools.w3schools_cleaner_instance,
    "geeksforgeeks.org": geeksforgeeks.geeksforgeeks_cleaner_instance,
    "docs.oracle.com": oracle.oracle_cleaner_instance,
}


def get_site_cleaner(url: str) -> Optional[BaseCleaner]:
    for domain, cleaner_instance in SITE_CLEANERS.items():
        if domain in url:
            return cleaner_instance
    return BaseCleaner()
