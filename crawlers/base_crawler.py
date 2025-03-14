from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
import datetime
import time
from fundus import Crawler, PublisherCollection, Sitemap, Article
from crawlers.helpers import display, print_divider


class BaseCrawler(ABC):
    def __init__(self, sources, max_articles: int, days: int, timeout_seconds: Optional[int] = None):
        # NOTE: adding restrict_sources_to=[Sitemap] makes The Guardian not work
        self.crawler = Crawler(*sources)
        self.max_articles = max_articles
        self.days = days
        self.timeout_seconds = timeout_seconds
        self.start_date = datetime.date.today() - datetime.timedelta(days=days)
        # TODO: Allow end date to be passed in instead of assuming it's today

    @abstractmethod
    def get_filter_params(self) -> Dict[str, Any]:
        pass

    def publishing_date_filter(self, extracted: Dict[str, Any]) -> bool:
        end_date = datetime.date.today() - datetime.timedelta(
            days=0
        )  # TODO: allowing a range of dates instead of forcing to end today would be nice
        start_date = end_date - datetime.timedelta(days=self.days)
        if publishing_date := extracted.get("publishing_date"):
            return not (start_date <= publishing_date.date() <= end_date)
        return True

    def run_crawler(self, display_output: bool = True) -> List[Article]:
        filter_params = self.get_filter_params()
        articles = []
        start_time = time.time()

        for article in self.crawler.crawl(
            max_articles=self.max_articles, **filter_params
        ):
            # Check timeout if specified
            if self.timeout_seconds and (time.time() - start_time) > self.timeout_seconds:
                if display_output:
                    print(f"\nTimeout reached after {self.timeout_seconds} seconds")
                    print_divider()
                break

            # URL filters don't check date because they only look at the URLs, so it's done here instead, which isn't ideal
            # But body filter does check date in advance, so this check is redundant for body filter
            if article.publishing_date.date() >= self.start_date:
                if display_output:
                    display(article)
                articles.append(article)
            elif self.max_articles:
                if display_output:
                    print("\n(Skipping display of older article.)")
                    print_divider()
            else:
                if display_output:
                    print(".")
        return articles
