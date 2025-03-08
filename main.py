import argparse
from fundus import PublisherCollection
from searches import BodyFilterCrawler, UrlFilterCrawler, SingleSourceCrawler

def main(crawler: str, max_articles: int, days_back: int):
    max_str = f" with max articles set to {max_articles}" if max_articles else " with no max article limit"
    print(f"Using {crawler} crawler for search{max_str} and going {days_back} day(s) back.\n")

    default_sources = (PublisherCollection.us, PublisherCollection.uk)

    if crawler == "body":
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
    parser.add_argument("crawler", choices=["body", "url", "ny", "guardian"], help="The type of crawler to use (body, url, ny, or guardian)")
    parser.add_argument("--max_articles", type=int, default=None, help="The maximum number of articles to retrieve (default: unlimited)")
    parser.add_argument("--days_back", type=int, default=7, help="The number of days back to search (default: 7)")
    args = parser.parse_args()
    main(args.crawler, args.max_articles, args.days_back)
