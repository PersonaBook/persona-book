# app/services/external_search_service.py
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List, Dict, Any, Optional
from app.core.config import settings


class ExternalSearchService:
    def __init__(self):
        self.service = build(
            "customsearch", "v1", developerKey=settings.google_search_api_key
        )
        self.cse_id = settings.google_cse_id

    async def search_learning_materials(
        self, query: str, num_results: int = 10, site_restrict: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Google Custom Search API를 사용하여 학습 자료를 검색합니다.
        site_restrict를 통해 특정 도메인으로 검색을 제한할 수 있습니다.
        """
        try:
            print(
                f"Searching Google for: '{query}' with site_restrict: {site_restrict}"
            )

            request_body = {
                "q": query,
                "cx": self.cse_id,
                "num": num_results,
            }

            search_results = self.service.cse().list(**request_body).execute()

            items = []
            for item in search_results.get("items", []):
                items.append(
                    {
                        "title": item.get("title", "No Title"),
                        "link": item.get("link"),
                        "snippet": item.get("snippet", ""),
                    }
                )
            print(f"Found {len(items)} search results.")
            return items
        except HttpError as e:
            print(f"Google Custom Search API error: {e}")
            if e.resp.status == 429:
                print("Rate limit exceeded for Google Custom Search API.")
            return []
        except Exception as e:
            print(f"An unexpected error occurred during Google Search: {e}")
            return []
