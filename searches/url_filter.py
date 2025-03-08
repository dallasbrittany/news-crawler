from typing import List
import datetime
from fundus import Crawler, PublisherCollection
from fundus.scraping.filter import inverse, regex_filter, lor, land
from searches.helpers import display1

class UrlFilterCrawler:
    def __init__(self, max_articles: int, filter_out_terms: str, filter_include_terms: List[str], days: int):
        self.crawler = Crawler(PublisherCollection.us)
        self.max_articles = max_articles
        self.filter_out_terms_list = filter_out_terms
        self.filter_include_terms_list = filter_include_terms
        self.days = days
        self.end_date = datetime.date.today() - datetime.timedelta(days=days)

    def run_crawler(self):
        filter_out_terms = "|".join(self.filter_out_terms_list)
        filter_out = regex_filter(filter_out_terms)

        filter_include_terms = [regex_filter(term) for term in self.filter_include_terms_list]
        filter_include = inverse(land(*filter_include_terms))

        for article in self.crawler.crawl(max_articles=self.max_articles, url_filter=lor(filter_out, filter_include)):
            # just not printing the ones with unwanted dates is a workaround
            if article.publishing_date.date() > self.end_date:
                display1(article)
            elif self.max_articles:
                # because of the workaround with filtering out dates, the max article count likely won't match the number of found articles, so printing this is helpful in that case
                print("\n(Skipping display of older article.)")
                print("-"*20)
