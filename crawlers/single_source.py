from typing import Dict, Any
from crawlers.base_crawler import BaseCrawler

class SingleSourceCrawler(BaseCrawler):
    def __init__(self, source, max_articles: int, days: int):
        super().__init__(source, max_articles, days)

    def get_filter_params(self) -> Dict[str, Any]:
        return {}

    def run_crawler(self):
        super().run_crawler()