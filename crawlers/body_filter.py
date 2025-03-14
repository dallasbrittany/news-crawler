from typing import Dict, List, Any
from fundus.scraping.filter import inverse, regex_filter, lor, land
from crawlers.base_crawler import BaseCrawler
from crawlers.helpers import print_divider
from fundus import Article


class BodyFilterCrawler(BaseCrawler):
    def __init__(
        self, sources, max_articles: int, days: int, body_search_terms: List[str]
    ):
        super().__init__(sources, max_articles, days)
        self.body_search_terms = body_search_terms

    def body_filter(self, extracted: Dict[str, Any]) -> bool:
        if body := extracted.get("body"):
            for word in self.body_search_terms:
                if word in str(body).casefold():
                    return False
        return True

    def get_filter_params(self) -> Dict[str, Any]:
        return {"only_complete": lor(self.publishing_date_filter, self.body_filter)}

    def run_crawler(self, display_output: bool = True) -> List[Article]:
        if display_output:
            print("body search terms", self.body_search_terms)
            print_divider()
        return super().run_crawler(display_output=display_output)
