from bs4.element import Tag
from typing import Set, Optional
from app.utils.crawler.sites.base import BaseCleaner


class OracleCleaner(BaseCleaner):
    def clean_paragraph(self, element: Tag, seen_blocks: Set[str]) -> Optional[str]:
        text = element.get_text(strip=True)
        normalized = " ".join(text.split())
        if normalized in seen_blocks:
            return None
        seen_blocks.add(normalized)
        return f"{normalized}\n"

    def clean_list_item(self, element: Tag, seen_blocks: Set[str]) -> Optional[str]:
        paragraph = element.find("p")
        if paragraph:
            text = paragraph.get_text(strip=True)
            normalized = " ".join(text.split())
            if normalized in seen_blocks:
                return None
            seen_blocks.add(normalized)
            return f"- {normalized}\n"
        else:
            return None

    def clean_code(self, code_content: str, seen_blocks: Set[str]) -> Optional[str]:
        return super().clean_code(code_content, seen_blocks)


oracle_cleaner_instance = OracleCleaner()
