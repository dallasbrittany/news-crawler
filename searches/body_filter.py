from typing import Dict, List, Any
from fundus import Crawler, PublisherCollection
import datetime
from searches.helpers import display, print_divider

class BodyFilterCrawler:
    def __init__(self, max_articles, days: int, body_search_terms: List[str]):
        self.crawler = Crawler(PublisherCollection.us)
        self.max_articles = max_articles
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
        print("body search terms", self.body_search_terms)
        print_divider()

        for article in self.crawler.crawl(max_articles=self.max_articles, only_complete=self.body_filter):
            # land(body_filter, date_filter) doesn't seem to work as expected, so just not printing the ones with unwanted dates is a workaround
            if article.publishing_date.date() > self.end_date:
                display(article)
            elif self.max_articles:
                # because of the workaround with filtering out dates, the max article count likely won't match the number of found articles, so printing this is helpful in that case
                print("\n(Skipping display of older article.)")
                print_divider()
