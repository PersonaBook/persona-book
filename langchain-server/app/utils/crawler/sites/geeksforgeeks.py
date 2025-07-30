import re
from typing import Set, Optional
from app.utils.crawler.sites.base import BaseCleaner


class GeeksForGeeksCleaner(BaseCleaner):
    def clean_code(self, code_content: str, seen_blocks: Set[str]) -> Optional[str]:
        code_content = re.sub(
            r"<span[^>]*>.*?</span>", "", code_content, flags=re.DOTALL
        )
        code_content = re.sub(
            r"Try it Yourself\s*\u00bb", "", code_content, flags=re.IGNORECASE
        )
        code_content = re.sub(r"\s+", " ", code_content).strip()

        normalized = re.sub(r"\s+", "", code_content.lower())
        if normalized in seen_blocks:
            return None
        seen_blocks.add(normalized)
        return code_content


geeksforgeeks_cleaner_instance = GeeksForGeeksCleaner()
