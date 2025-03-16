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
        is_url_search: bool = False,
    ):
        # Skip the parent class __init__ since we don't need the actual crawler
        self.sources = sources if isinstance(sources, (list, tuple)) else [sources]
        self.max_articles = max_articles
        self.days = days
        self.search_terms = search_terms
        self.exclude_terms = exclude_terms or []
        self.timeout_seconds = timeout_seconds
        self.is_url_search = is_url_search

    def _extract_source_names(self, sources) -> List[str]:
        """Extract source names from source objects or collections."""
        source_names = set()
        for source in sources:
            # If it's a collection (like PublisherCollection.us)
            if hasattr(source, '__dict__'):
                for name, publisher in vars(source).items():
                    if not name.startswith('__') and hasattr(publisher, 'name'):
                        source_names.add(publisher.name)
            # If it's a direct publisher object
            elif hasattr(source, 'name'):
                source_names.add(source.name)
            # If it's already a string
            elif isinstance(source, str):
                source_names.add(source)
        return list(source_names)

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

        # Get source names
        source_names = self._extract_source_names(self.sources)
        if display_output:
            print(f"Using sources: {source_names}")

        articles = get_mock_articles(
            include_terms=self.search_terms,
            exclude_terms=self.exclude_terms,
            max_articles=self.max_articles,
            days_back=self.days,
            sources=source_names,
            is_url_search=self.is_url_search,
        )

        if display_output:
            print(f"\nFound {len(articles)} mock article(s)")

        return articles
