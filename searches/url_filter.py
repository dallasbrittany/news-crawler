from typing import List
from fundus import Crawler, PublisherCollection
from fundus.scraping.filter import inverse, regex_filter, lor, land
from searches.helpers import display1

class UrlFilterCrawler:
    def __init__(self, max_articles: int, filter_out_terms: str, filter_include_terms: List[str]):
        self.crawler = Crawler(PublisherCollection.us)
        self.max_articles = max_articles
        self.filter_out_terms_list = filter_out_terms
        self.filter_include_terms_list = filter_include_terms

    def run_crawler(self):
        filter_out_terms = "|".join(self.filter_out_terms_list)
        filter_out = regex_filter(filter_out_terms)

        filter_include_terms = [regex_filter(term) for term in self.filter_include_terms_list]
        filter_include = inverse(land(*filter_include_terms))

        for article in self.crawler.crawl(max_articles=self.max_articles, url_filter=lor(filter_out, filter_include)):
            display1(article)
