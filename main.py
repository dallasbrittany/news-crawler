import argparse
from searches.body_filter import BodyFilterCrawler
from searches.url_filter import UrlFilterCrawler

def main(crawler: str):
    max_articles = None # unlimited with None
    max_str = f" with max articles set to {max_articles}" if max_articles else " with no max article limit"
    print(f"Using {crawler} crawler for search{max_str}.\n")
    if crawler == "filter":
        body_search_terms = ["pollution", "climate crisis", "environmental"]
        days_back = 1
        crawler = BodyFilterCrawler(max_articles, body_search_terms, days_back)
        crawler.run_crawler()
    elif crawler == "url":
        filter_out_terms = ["advertisement", "podcast"]
        filter_include_terms = ["coral", "climate"]
        url_filter_crawler = UrlFilterCrawler(max_articles, filter_out_terms, filter_include_terms)
        url_filter_crawler.run_crawler()
    else:
        raise ValueError(f"Unknown crawler type: {crawler}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the news crawler.")
    parser.add_argument("crawler", choices=["filter", "url"], help="The type of crawler to use (filter or url)")
    args = parser.parse_args()
    main(args.crawler)
