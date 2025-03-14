from typing import Dict, Any, Optional, List
from crawlers.base_crawler import BaseCrawler
from fundus import Article


class SingleSourceCrawler(BaseCrawler):
    def __init__(
        self,
        source,
        max_articles: int,
        days: int,
        timeout_seconds: Optional[int] = None,
    ):
        super().__init__(source, max_articles, days, timeout_seconds=timeout_seconds)

    def get_filter_params(self) -> Dict[str, Any]:
        return {"only_complete": self.publishing_date_filter}

    def run_crawler(self, display_output: bool = True) -> List[Article]:
        return super().run_crawler(display_output=display_output)
