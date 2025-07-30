import re
from typing import Set, Optional
from app.utils.crawler.sites.base import BaseCleaner


class W3SchoolsCleaner(BaseCleaner):
    def clean_code(self, code_content: str, seen_blocks: Set[str]) -> Optional[str]:
        code_content = re.sub(
            r"^(Example|### Example)\s*", "", code_content, flags=re.IGNORECASE
        )
        code_content = re.sub(
            r"Try it Yourself\s*»", "", code_content, flags=re.IGNORECASE
        )
        code_content = re.sub(r"\s+", " ", code_content).strip()

        normalized_code = re.sub(r"\s+", "", code_content.lower())
        if normalized_code in seen_blocks:
            return None
        seen_blocks.add(normalized_code)

        return code_content


w3schools_cleaner_instance = W3SchoolsCleaner()
