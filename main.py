import argparse
import uvicorn
from fundus import PublisherCollection
from crawlers import BodyFilterCrawler, UrlFilterCrawler
from crawlers.helpers import print_exclude_not_implemented
from typing import Optional, List


def get_sources(source_names: Optional[List[str]] = None):
    if not source_names:
        return (
            PublisherCollection.us,
            PublisherCollection.uk,
            PublisherCollection.au,
            PublisherCollection.ca,
        )

    # Get all sources but filter out Python's built-in attributes
    valid_sources = {
        name: source
        for collection in [
            PublisherCollection.us,
            PublisherCollection.uk,
            PublisherCollection.au,
            PublisherCollection.ca,
        ]
        for name, source in vars(collection).items()
        if not name.startswith("__")
    }

    invalid_sources = [name for name in source_names if name not in valid_sources]
    if invalid_sources:
        available_sources = sorted(valid_sources.keys())
        raise ValueError(
            f"Invalid source(s): {', '.join(invalid_sources)}\n"
            f"Available sources are: {', '.join(available_sources)}"
        )

    sources = []
    for name in source_names:
        if hasattr(PublisherCollection.us, name):
            sources.append(getattr(PublisherCollection.us, name))
        elif hasattr(PublisherCollection.uk, name):
            sources.append(getattr(PublisherCollection.uk, name))
        elif hasattr(PublisherCollection.au, name):
            sources.append(getattr(PublisherCollection.au, name))
        elif hasattr(PublisherCollection.ca, name):
            sources.append(getattr(PublisherCollection.ca, name))
    return tuple(sources)


def main(
    crawler: str,
    max_articles: int,
    days_back: int,
    keywords_include: list,
    keywords_exclude: list,
    timeout: Optional[int] = None,
    sources: Optional[List[str]] = None,
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
    print(
        f"Using {crawler} crawler for search{sources_str}{max_str} and going {days_back} day(s) back{timeout_str}.\n"
    )

    crawler_sources = get_sources(sources)

    if crawler == "body":
        if not keywords_include:
            raise ValueError("keywords_include is required for body search")

        if keywords_exclude:
            print_exclude_not_implemented()

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
    parser.add_argument(
        "--sources",
        nargs="+",
        help="List of news sources to crawl (e.g., TheNewYorker, TheGuardian). If not specified, uses all US and UK sources",
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
        )
    else:  # api mode
        from api import app

        print(f"Starting API server on {args.host}:{args.port}")
        print("API documentation available at http://127.0.0.1:8000/docs")
        uvicorn.run(app, host=args.host, port=args.port)
