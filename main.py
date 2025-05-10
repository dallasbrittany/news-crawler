import argparse
import uvicorn
from fundus import PublisherCollection
from crawlers import BodyFilterCrawler, UrlFilterCrawler
from crawlers.helpers import print_exclude_not_implemented
from typing import Optional, List
from crawlers.base_crawler import (
    CrawlerError,
    NetworkError,
    TimeoutError,
    PUBLISHER_COLLECTIONS,
    PUBLISHER_COLLECTIONS_LIST,
)


def normalize_source_name(name: str) -> str:
    """Normalize source name by removing spaces and special characters."""
    return "".join(name.split())


def get_sources(source_names: Optional[List[str]] = None):
    if not source_names:
        return (
            PublisherCollection.us,
            PublisherCollection.uk,
            PublisherCollection.au,
            PublisherCollection.ca,
        )

    # Create a mapping of normalized names to actual source objects
    source_mapping = {}
    for collection in PUBLISHER_COLLECTIONS_LIST:
        for name, source in vars(collection).items():
            if not name.startswith("__"):
                source_mapping[normalize_source_name(name)] = (name, source)

    sources = []
    invalid_sources = []
    for name in source_names:
        normalized_name = normalize_source_name(name)
        if normalized_name in source_mapping:
            original_name, source = source_mapping[normalized_name]
            sources.append(source)
            print(f"Found {name} (matched as {original_name})")
        else:
            invalid_sources.append(name)

    if invalid_sources:
        # Get list of valid sources with their display names
        valid_sources = {}
        for collection in PUBLISHER_COLLECTIONS_LIST:
            for name, source in vars(collection).items():
                if not name.startswith("__"):
                    display_name = " ".join(
                        word for word in name if word.isupper() or word == name[0]
                    )
                    valid_sources[name] = display_name

        valid_source_display = [
            f"{display} ({name})" for name, display in valid_sources.items()
        ]
        raise ValueError(
            f"Invalid source(s): {', '.join(invalid_sources)}.\n"
            f"Valid sources are: {', '.join(sorted(valid_source_display))}"
        )

    return tuple(sources)


def main(
    crawler: str,
    max_articles: int,
    days_back: int,
    keywords_include: list,
    keywords_exclude: list,
    timeout: Optional[int] = None,
    sources: Optional[List[str]] = None,
    use_mock: bool = False,
):
    max_str = (
        f" with max articles set to {max_articles}"
        if max_articles
        else " with no max article limit"
    )
    timeout_str = f" with a timeout of {timeout} seconds" if timeout else ""
    sources_str = (
        f" from {', '.join(sources)}"
        if sources
        else " from all US, UK, Australian, and Canadian sources"
    )
    mock_str = " (using mock data)" if use_mock else ""
    print(
        f"Using {crawler} crawler for search{sources_str}{max_str} and going {days_back} day(s) back{timeout_str}{mock_str}.\n"
    )

    crawler_sources = get_sources(sources)

    if crawler == "body":
        if not keywords_include:
            raise ValueError("keywords_include is required for body search")

        if keywords_exclude:
            print_exclude_not_implemented()

        if use_mock:
            from crawlers.mock_crawler import MockCrawler

            crawler = MockCrawler(
                crawler_sources,
                max_articles,
                days_back,
                keywords_include,
                timeout_seconds=timeout,
                is_url_search=False,  # Body search
            )
        else:
            from crawlers import BodyFilterCrawler

            crawler = BodyFilterCrawler(
                crawler_sources,
                max_articles,
                days_back,
                keywords_include,
                timeout_seconds=timeout,
            )
        crawler.run_crawler()
    elif crawler == "url":
        if not keywords_include:
            raise ValueError("keywords_include is required for URL search")

        if use_mock:
            from crawlers.mock_crawler import MockCrawler

            url_filter_crawler = MockCrawler(
                crawler_sources,
                max_articles,
                days_back,
                keywords_include,
                keywords_exclude or [],
                timeout_seconds=timeout,
                is_url_search=True,  # URL search
            )
        else:
            from crawlers import UrlFilterCrawler

            url_filter_crawler = UrlFilterCrawler(
                crawler_sources,
                max_articles,
                days_back,
                keywords_include,
                keywords_exclude or [],
                timeout_seconds=timeout,
            )
        url_filter_crawler.run_crawler()
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
        "--exclude", nargs="+", help="List of keywords to exclude from URL search"
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
    parser.add_argument(
        "--sources",
        nargs="+",
        help="List of news sources to crawl (e.g., TheNewYorker, TheGuardian). If not specified, uses all US and UK sources",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Use mock data instead of real crawling (for testing)",
    )

    args = parser.parse_args()

    if args.mode == "cli":
        if not args.crawler:
            parser.error("CLI mode requires --crawler argument")
        main(
            args.crawler,
            args.max_articles,
            args.days_back,
            args.include,
            args.exclude,
            args.timeout,
            args.sources,
            args.mock,
        )
    else:  # api mode
        from api import app

        print(f"Starting API server on {args.host}:{args.port}")
        print("API documentation available at http://127.0.0.1:8000/docs")
        if args.mock:
            print("Running in mock mode - using test data instead of real crawling")
            app.state.use_mock = True
        uvicorn.run(app, host=args.host, port=args.port)
