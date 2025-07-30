from typing import Optional, Set
from bs4.element import Tag


class BaseCleaner:
    def clean_code(self, code_content: str, seen_blocks: Set[str]) -> Optional[str]:
        code_content = code_content.strip()
        normalized_code = " ".join(code_content.split()).lower()
        if normalized_code in seen_blocks:
            return None
        seen_blocks.add(normalized_code)
        return code_content

    def clean_paragraph(self, element: Tag, seen_blocks: Set[str]) -> Optional[str]:
        text = element.get_text(strip=True)
        normalized = " ".join(text.split())
        if normalized in seen_blocks:
            return None
        seen_blocks.add(normalized)
        return f"{normalized}\n"

    def clean_list_item(self, element: Tag, seen_blocks: Set[str]) -> Optional[str]:
        text = element.get_text(strip=True)
        normalized = " ".join(text.split())
        if normalized in seen_blocks:
            return None
        seen_blocks.add(normalized)
        return f"- {normalized}\n"
