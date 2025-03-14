from typing import Dict, Any, List
from fundus.scraping.filter import inverse, regex_filter, lor, land
from crawlers.base_crawler import BaseCrawler
from crawlers.helpers import display, print_divider
from fundus import Article


class UrlFilterCrawler(BaseCrawler):
    def __init__(
        self,
        sources,
        max_articles: int,
        days: int,
        filter_include_terms: List[str],
        filter_out_terms: List[str],
    ):
        super().__init__(sources, max_articles, days)
        self.filter_out_terms_list = filter_out_terms
        self.filter_include_terms_list = filter_include_terms

    def get_filter_params(self) -> Dict[str, Any]:
        filter_out_terms = "|".join(self.filter_out_terms_list)
        filter_out = regex_filter(filter_out_terms)

        filter_include_terms = [
            regex_filter(term) for term in self.filter_include_terms_list
        ]
        filter_include = inverse(land(*filter_include_terms))

        return {"url_filter": lor(filter_out, filter_include)}

    def run_crawler(self, display_output: bool = True) -> List[Article]:
        if display_output:
            print("filter include terms", self.filter_include_terms_list)
            print("filter out terms", self.filter_out_terms_list)
            print_divider()

        return super().run_crawler(display_output=display_output)
