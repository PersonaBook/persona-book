import requests
from bs4 import BeautifulSoup
import re
from typing import Optional
from app.utils.crawler.sites import get_site_cleaner


def extract_text_from_url(url: str) -> Optional[str]:
    """
    주어진 URL에서 주요 텍스트 콘텐츠를 추출합니다.
    사이트별 특정 태그를 사용하여 메인 콘텐츠를 찾고, 불필요한 태그를 제거합니다.
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(
            [
                "script",
                "style",
                "noscript",
                "header",
                "footer",
                "nav",
                "aside",
                "form",
                "iframe",
                "img",
                "link",
            ]
        ):
            tag.decompose()

        main_content = None
        if "baeldung.com" in url:
            main_content = soup.find("article")
        elif "aws.amazon.com" in url:
            main_content = soup.find("div", class_="lb-col") or soup.find("main")
        elif "ibm.com" in url:
            main_content = soup.find(
                "div", class_="ibm-col-resource-content"
            ) or soup.find("main")
        elif "w3schools.com" in url:
            main_content = soup.find("div", id="main") or soup.find(
                "div", id="maincontent"
            )
        elif "geeksforgeeks.org" in url:
            main_content = soup.find("div", class_="text") or soup.find("article")
        elif "azure.microsoft.com" in url:
            main_content = soup.find("main")
        elif "javapedia.net" in url:
            main_content = soup.find("div", class_="content")
        elif "docs.oracle.com" in url:
            main_content = soup.find("div", class_="body-content") or soup.find("main")

        if not main_content:
            main_content = soup.find("body")
        if not main_content:
            return None

        text_parts = []
        seen_code_blocks = set()
        site_cleaner = get_site_cleaner(url)

        for element in main_content.find_all(
            ["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "pre", "code", "div"]
        ):
            if element.name.startswith("h"):
                text_parts.append(
                    f"\n{'#' * int(element.name[1])} {element.get_text(strip=True)}\n"
                )
            elif element.name == "p":
                if site_cleaner and hasattr(site_cleaner, "clean_paragraph"):
                    cleaned_p = site_cleaner.clean_paragraph(element, seen_code_blocks)
                    if cleaned_p:
                        text_parts.append(cleaned_p)
                else:
                    text_parts.append(f"{element.get_text(strip=True)}\n")
            elif element.name == "li":
                if site_cleaner and hasattr(site_cleaner, "clean_list_item"):
                    cleaned_li = site_cleaner.clean_list_item(element, seen_code_blocks)
                    if cleaned_li:
                        text_parts.append(cleaned_li)
                else:
                    text_parts.append(f"- {element.get_text(strip=True)}\n")
            elif element.name == "pre":
                code_tag = element.find("code")
                code_content = (
                    code_tag.get_text(strip=False).strip()
                    if code_tag
                    else element.get_text(strip=False).strip()
                )

                if site_cleaner and hasattr(site_cleaner, "clean_code"):
                    code_content = site_cleaner.clean_code(
                        code_content, seen_code_blocks
                    )

                if code_content:
                    text_parts.append(f"\n```java\n{code_content}\n```\n")
            elif element.name == "code" and not element.find_parent("pre"):
                text_parts.append(f"`{element.get_text(strip=True)}`")
            elif element.name == "div":
                text_content = element.get_text(strip=True)
                if text_content:
                    text_parts.append(f"{text_content}\n")

        clean_text = "\n".join(text_parts)
        clean_text = re.sub(r"\n\s*\n", "\n\n", clean_text)
        clean_text = re.sub(r" +", " ", clean_text).strip()
        return clean_text

    except requests.exceptions.RequestException as req_err:
        print(f"Request error for {url}: {req_err}")
        return None
    except Exception as e:
        print(f"Crawling or parsing error for {url}: {e}")
        return None
