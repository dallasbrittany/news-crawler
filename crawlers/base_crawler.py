from typing import Dict, Any
from abc import ABC, abstractmethod
import datetime
from fundus import Crawler, PublisherCollection, Sitemap
from crawlers.helpers import display, print_divider


class BaseCrawler(ABC):
    def __init__(self, sources, max_articles: int, days: int):
        # NOTE: adding restrict_sources_to=[Sitemap] makes The Guardian not work
        self.crawler = Crawler(*sources)
        self.max_articles = max_articles
        self.days = days
        self.end_date = datetime.date.today() - datetime.timedelta(days=days)

    @abstractmethod
    def get_filter_params(self) -> Dict[str, Any]:
        pass

    def run_crawler(self):
        filter_params = self.get_filter_params()
        for article in self.crawler.crawl(
            max_articles=self.max_articles, **filter_params
        ):
            if article.publishing_date.date() > self.end_date:
                display(article)
            elif self.max_articles:
                print("\n(Skipping display of older article.)")
                print_divider()
            else:
                print(".")
