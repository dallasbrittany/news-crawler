import argparse
from fundus import PublisherCollection
from searches import BodyFilterCrawler, UrlFilterCrawler, SingleSourceCrawler

def main(crawler: str):
    max_articles = None # unlimited with None
    days_back = 7

    max_str = f" with max articles set to {max_articles}" if max_articles else " with no max article limit"
    print(f"Using {crawler} crawler for search{max_str} and going {days_back} day(s) back.\n")

    default_sources = (PublisherCollection.us, PublisherCollection.uk)

    if crawler == "filter":
        # matches on any of these terms in the body
        terms_environment = ["pollution", "environmental", "climate crisis", "EPA", "coral", "reef"]
        terms_us_politics = ["trump"]
        body_search_terms = terms_environment

        crawler = BodyFilterCrawler(default_sources, max_articles, days_back, body_search_terms)
        crawler.run_crawler()
    elif crawler == "url":
        # must match on all the required terms in the URL
        required_terms = ["coral", "climate"]
        # required_terms = ["trump"]

        filter_out_terms = ["advertisement", "podcast"]

        url_filter_crawler = UrlFilterCrawler(default_sources, max_articles, days_back, required_terms, filter_out_terms)
        url_filter_crawler.run_crawler()
    elif crawler == "ny":
        source = (PublisherCollection.us.TheNewYorker) # (PublisherCollection.uk.TheGuardian)
        crawler = SingleSourceCrawler([source], max_articles, days_back)
        crawler.run_crawler()
    elif crawler == "guardian":
        source = (PublisherCollection.uk.TheGuardian)
        crawler = SingleSourceCrawler([source], max_articles, days_back)
        crawler.run_crawler()
    else:
        raise ValueError(f"Unknown crawler type: {crawler}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the news crawler.")
    parser.add_argument("crawler", choices=["filter", "url", "ny", "guardian"], help="The type of crawler to use (filter, url, ny, or guardian)")
    args = parser.parse_args()
    main(args.crawler)
