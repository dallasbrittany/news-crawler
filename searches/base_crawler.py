from typing import Dict, Any
from abc import ABC, abstractmethod
import datetime
from fundus import Crawler, PublisherCollection, Sitemap
from searches.helpers import display, print_divider

class BaseCrawler(ABC):
    def __init__(self, max_articles: int, days: int):
        self.crawler = Crawler(PublisherCollection.us, PublisherCollection.uk, restrict_sources_to=[Sitemap])
        self.max_articles = max_articles
        self.days = days
        self.end_date = datetime.date.today() - datetime.timedelta(days=days)

    @abstractmethod
    def get_crawl_params(self) -> Dict[str, Any]:
        pass

    def run_crawler(self):
        crawl_params = self.get_crawl_params()
        for article in self.crawler.crawl(max_articles=self.max_articles, **crawl_params):
            if article.publishing_date.date() > self.end_date:
                display(article)
            elif self.max_articles:
                print("\n(Skipping display of older article.)")
                print_divider()
