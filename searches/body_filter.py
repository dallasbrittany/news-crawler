from typing import Dict, List, Any
from fundus import Crawler, PublisherCollection
import datetime
from searches.helpers import display1

class BodyFilterCrawler:
    def __init__(self, body_search_terms: List[str], days: int):
        self.crawler = Crawler(PublisherCollection.us)
        self.body_search_terms = body_search_terms
        self.days = days
        self.end_date = datetime.date.today() - datetime.timedelta(days=days)

    def body_filter(self, extracted: Dict[str, Any]) -> bool:
        if body := extracted.get("body"):
            for word in self.body_search_terms:
                if word in str(body).casefold():
                    return False
        return True

    def run_crawler(self):
        for article in self.crawler.crawl(only_complete=self.body_filter):
            # land(body_filter, date_filter) doesn't seem to work as expected, so just not printing the ones with unwanted dates is a workaround
            if article.publishing_date.date() > self.end_date:
                display1(article)
