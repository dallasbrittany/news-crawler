import argparse
import uvicorn
from fundus import PublisherCollection
from crawlers import BodyFilterCrawler, UrlFilterCrawler, SingleSourceCrawler
from crawlers.helpers import (
    print_include_not_implemented,
    print_exclude_not_implemented,
)
from typing import Optional


def main(
    crawler: str,
    max_articles: int,
    days_back: int,
    keywords_include: list,
    keywords_exclude: list,
    timeout: Optional[int] = None,
):
    max_str = (
        f" with max articles set to {max_articles}"
        if max_articles
        else " with no max article limit"
    )
    timeout_str = f" with a timeout of {timeout} seconds" if timeout else ""
    print(
        f"Using {crawler} crawler for search{max_str} and going {days_back} day(s) back{timeout_str}.\n"
    )

    default_sources = (PublisherCollection.us, PublisherCollection.uk)

    if crawler == "body":
        # matches on any of these terms in the body
        terms_default = [
            "pollution",
            "environmental",
            "climate crisis",
            "EPA",
            "coral",
            "reef",
        ]
        body_search_terms = keywords_include if keywords_include else terms_default
        if keywords_exclude:
            print_exclude_not_implemented()

        crawler = BodyFilterCrawler(
            default_sources, max_articles, days_back, body_search_terms, timeout_seconds=timeout
        )
        crawler.run_crawler()
    elif crawler == "url":
        # must match on all the required terms in the URL
        required_terms_default = ["coral", "climate"]
        required_terms = (
            keywords_include if keywords_include else required_terms_default
        )

        filter_out_terms_default = ["advertisement", "podcast"]
        filter_out_terms = (
            keywords_exclude if keywords_exclude else filter_out_terms_default
        )

        url_filter_crawler = UrlFilterCrawler(
            default_sources, max_articles, days_back, required_terms, filter_out_terms, timeout_seconds=timeout
        )
        url_filter_crawler.run_crawler()
    elif crawler == "ny":
        if keywords_include:
            print_include_not_implemented()
        if keywords_exclude:
            print_exclude_not_implemented()
        source = PublisherCollection.us.TheNewYorker
        crawler = SingleSourceCrawler([source], max_articles, days_back, timeout_seconds=timeout)
        crawler.run_crawler()
    elif crawler == "guardian":
        if keywords_include:
            print_include_not_implemented()
        if keywords_exclude:
            print_exclude_not_implemented()
        source = PublisherCollection.uk.TheGuardian
        crawler = SingleSourceCrawler([source], max_articles, days_back, timeout_seconds=timeout)
        crawler.run_crawler()
    else:
        raise ValueError(f"Unknown crawler type: {crawler}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the news crawler.")
    parser.add_argument(
        "mode",
        choices=["cli", "api"],
        help="Run in CLI mode or start the API server",
    )
    parser.add_argument(
        "--crawler",
        choices=["body", "url", "ny", "guardian"],
        help="The type of crawler to use (body, url, ny, or guardian)",
    )
    parser.add_argument(
        "--max_articles",
        type=int,
        default=None,
        help="The maximum number of articles to retrieve (default: unlimited)",
    )
    parser.add_argument(
        "--days_back",
        type=int,
        default=7,
        help="The number of days back to search (default: 7)",
    )
    parser.add_argument(
        "--include", nargs="+", help="List of keywords to include in the search"
    )
    parser.add_argument(
        "--exclude", nargs="+", help="List of keywords to exclude from the search"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=None,
        help="Maximum number of seconds to run the query (default: no timeout)",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to run the API server on (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to run the API server on (default: 8000)",
    )

    args = parser.parse_args()

    if args.mode == "cli":
        if not args.crawler:
            parser.error("CLI mode requires --crawler argument")
        main(args.crawler, args.max_articles, args.days_back, args.include, args.exclude, args.timeout)
    else:  # api mode
        from api import app
        print(f"Starting API server on {args.host}:{args.port}")
        print("API documentation available at http://127.0.0.1:8000/docs")
        uvicorn.run(app, host=args.host, port=args.port)
