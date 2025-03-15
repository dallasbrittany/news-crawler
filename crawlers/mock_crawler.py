from typing import Dict, List, Any, Optional
from .base_crawler import BaseCrawler
from .mock_data import get_mock_articles
from fundus import Article


class MockCrawler(BaseCrawler):
    def __init__(
        self,
        sources,
        max_articles: int,
        days: int,
        search_terms: List[str],
        exclude_terms: Optional[List[str]] = None,
        timeout_seconds: Optional[int] = None,
    ):
        # Skip the parent class __init__ since we don't need the actual crawler
        self.sources = sources if isinstance(sources, (list, tuple)) else [sources]
        self.max_articles = max_articles
        self.days = days
        self.search_terms = search_terms
        self.exclude_terms = exclude_terms or []
        self.timeout_seconds = timeout_seconds

    def get_filter_params(self) -> Dict[str, Any]:
        # Not used in mock crawler
        return {}

    def run_crawler(
        self, display_output: bool = True, show_body: bool = True
    ) -> List[Article]:
        if display_output:
            print("Using mock crawler with search terms:", self.search_terms)
            if self.exclude_terms:
                print("Exclude terms:", self.exclude_terms)

        # Convert sources to source names if needed
        source_names = []
        for source in self.sources:
            if hasattr(source, "name"):
                source_names.append(source.name)
            else:
                source_names.append(str(source))

        articles = get_mock_articles(
            include_terms=self.search_terms,
            exclude_terms=self.exclude_terms,
            max_articles=self.max_articles,
            days_back=self.days,
            sources=source_names if source_names else None,
        )

        if display_output:
            print(f"\nFound {len(articles)} mock articles")

        return articles
