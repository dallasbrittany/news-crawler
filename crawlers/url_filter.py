from typing import Dict, Any, List, Optional
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
        timeout_seconds: Optional[int] = None,
    ):
        super().__init__(sources, max_articles, days, timeout_seconds=timeout_seconds)
        self.filter_out_terms_list = filter_out_terms
        self.filter_include_terms_list = filter_include_terms

    def get_filter_params(self) -> Dict[str, Any]:
        filter_include_terms = [
            regex_filter(term) for term in self.filter_include_terms_list
        ]
        filter_include = inverse(land(*filter_include_terms))

        # Only use filter_out if there are actual terms to filter out
        if self.filter_out_terms_list and len(self.filter_out_terms_list) > 0:
            filter_out_terms = "|".join(self.filter_out_terms_list)
            filter_out = regex_filter(filter_out_terms)
            return {"url_filter": lor(filter_out, filter_include)}
        return {"url_filter": filter_include}

    def run_crawler(
        self, display_output: bool = True, show_body: bool = True
    ) -> List[Article]:
        if display_output:
            print("filter include terms", self.filter_include_terms_list)
            print("filter out terms", self.filter_out_terms_list)
            print_divider()

        return super().run_crawler(display_output=display_output, show_body=show_body)
