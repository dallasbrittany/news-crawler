from fastapi import FastAPI, Query, HTTPException, Depends
from fastapi.concurrency import run_in_threadpool
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, field_validator, Field
from datetime import datetime
from fundus import PublisherCollection, Article
from crawlers import BodyFilterCrawler, UrlFilterCrawler
from crawlers.base_crawler import (
    CrawlerError,
    NetworkError,
    TimeoutError,
    PUBLISHER_COLLECTIONS,
)

app = FastAPI(
    title="News Crawler API",
    description="API for crawling news articles from various sources",
    version="1.0.0",
)


class ArticleResponse(BaseModel):
    title: str
    url: str
    publishing_date: datetime
    body: str
    authors: Optional[List[str]] = []  # Made optional with default empty list
    source: str


class CrawlerResponse(BaseModel):
    articles: List[ArticleResponse]
    message: str = "Success"  # Added default value
    error: Optional[str] = None


class CrawlerParams(BaseModel):
    max_articles: Optional[int] = Field(
        None, ge=1, description="Maximum number of articles to retrieve"
    )
    days_back: int = Field(7, ge=1, description="Number of days back to search")
    timeout: Optional[int] = Field(
        25, ge=1, description="Maximum number of seconds to run the query (default: 25)"
    )
    sources: Optional[List[str]] = Field(
        None,
        description="List of sources to crawl (e.g., ['TheNewYorker', 'TheGuardian']). If not specified, uses all US, UK, Australian, and Canadian sources",
    )

    @field_validator("days_back")
    def validate_days_back(cls, v):
        if v <= 0:
            raise ValueError("days_back must be greater than 0")
        return v

    @field_validator("sources")
    def validate_sources(cls, v):
        if not v:
            return None

        # Create a mapping of normalized names to actual source names
        source_mapping = {}
        for collection in [
            PublisherCollection.us,
            PublisherCollection.uk,
            PublisherCollection.au,
            PublisherCollection.ca,
        ]:
            for name, source in vars(collection).items():
                if not name.startswith("__"):
                    source_mapping[normalize_source_name(name)] = name

        invalid_sources = []
        for source in v:
            normalized_name = normalize_source_name(source)
            if normalized_name not in source_mapping:
                invalid_sources.append(source)

        if invalid_sources:
            # Get list of valid sources with their display names
            valid_sources = {}
            for collection in [
                PublisherCollection.us,
                PublisherCollection.uk,
                PublisherCollection.au,
                PublisherCollection.ca,
            ]:
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
                f"Invalid source(s): {', '.join(invalid_sources)}. "
                f"Valid sources are: {', '.join(sorted(valid_source_display))}"
            )
        return v


def handle_crawler_error(e: Exception) -> Dict[str, Any]:
    if isinstance(e, TimeoutError):
        raise HTTPException(status_code=408, detail=str(e))
    elif isinstance(e, NetworkError):
        raise HTTPException(status_code=503, detail=str(e))
    elif isinstance(e, CrawlerError):
        raise HTTPException(status_code=500, detail=str(e))
    else:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


def article_to_dict(article: Article) -> Dict[str, Any]:
    """Convert an article to a dictionary format matching ArticleResponse."""
    try:
        # Ensure publishing_date is a datetime object
        if isinstance(article.publishing_date, str):
            # If it's a string, try to parse it as a datetime
            pub_date = datetime.fromisoformat(
                article.publishing_date.replace("Z", "+00:00")
            )
        else:
            # If it's already a datetime or similar, use it as is
            pub_date = article.publishing_date

        return {
            "title": article.title,
            "url": (
                article.url if hasattr(article, "url") else article.html.requested_url
            ),
            "publishing_date": pub_date,
            "body": article.body,
            "authors": getattr(article, "authors", []),
            "source": article.source if hasattr(article, "source") else "",
        }
    except AttributeError as e:
        print(f"Error processing article: {str(e)}")
        raise HTTPException(
            status_code=422, detail=f"Error processing article data: {str(e)}"
        )


def normalize_source_name(name: str) -> str:
    """Normalize source name by removing spaces and special characters."""
    return "".join(name.split())


def get_sources(source_names: Optional[List[str]] = None):
    if not source_names:
        sources = [
            source
            for collection in PUBLISHER_COLLECTIONS.values()
            for name, source in vars(collection).items()
            if not name.startswith("__")
        ]
        print(f"No sources specified, returning all sources: {len(sources)} sources")
        return sources

    print(f"Requested sources: {source_names}")
    sources = []
    invalid_sources = []

    # Create a mapping of normalized names to actual source names
    source_mapping = {}
    for collection in PUBLISHER_COLLECTIONS.values():
        for name, source in vars(collection).items():
            if not name.startswith("__"):
                source_mapping[normalize_source_name(name)] = (name, source)

    for name in source_names:
        normalized_name = normalize_source_name(name)
        if normalized_name in source_mapping:
            original_name, source = source_mapping[normalized_name]
            sources.append(source)
            print(f"Found {name} (matched as {original_name})")
        else:
            invalid_sources.append(name)
            print(f"Source not found: {name}")

    if invalid_sources:
        # Get list of valid sources with their display names
        valid_sources = {}
        for collection in PUBLISHER_COLLECTIONS.values():
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
            f"Invalid source(s): {', '.join(invalid_sources)}. "
            f"Valid sources are: {', '.join(sorted(valid_source_display))}"
        )

    if not sources:
        raise ValueError("No valid sources provided")

    print(
        f"Returning {len(sources)} sources: {[s.name if hasattr(s, 'name') else str(s) for s in sources]}"
    )
    return sources


def parse_sources(
    sources_param: Optional[str], params_sources: Optional[List[str]]
) -> Optional[List[str]]:
    """Parse sources from either comma-separated string or params list."""
    if sources_param:
        return [s.strip() for s in sources_param.split(",")]
    return params_sources


def expand_terms(terms: List[str]) -> List[str]:
    """Split comma-separated terms into individual terms and clean them."""
    expanded = []
    for term in terms:
        if "," in term:
            expanded.extend(t.strip() for t in term.split(",") if t.strip())
        else:
            if term.strip():
                expanded.append(term.strip())
    return expanded


async def handle_crawler_request(
    params: CrawlerParams,
    include: List[str],
    exclude: Optional[List[str]],
    sources: Optional[str],
    crawler_class,
) -> CrawlerResponse:
    try:
        print(f"API received timeout parameter: {params.timeout} seconds")
        print(f"Include terms: {include}")
        if exclude:
            print(f"Exclude terms: {exclude}")

        # Parse and validate sources
        sources_list = parse_sources(sources, params.sources)
        print(f"Parsed sources: {sources_list}")

        if app.state.use_mock:
            from crawlers.mock_crawler import MockCrawler

            crawler = MockCrawler(
                sources_list,  # Pass the source names directly
                params.max_articles,
                params.days_back,
                include,
                exclude,
                timeout_seconds=params.timeout,
            )
        else:
            sources = get_sources(sources_list)
            crawler = crawler_class(
                sources,
                params.max_articles,
                params.days_back,
                include,
                exclude if crawler_class.__name__ == "UrlFilterCrawler" else None,
                timeout_seconds=params.timeout,
            )

        articles = await run_in_threadpool(crawler.run_crawler, display_output=True)
        print(f"Crawler returned {len(articles)} articles")

        # Process articles
        processed_articles = []
        for article in articles:
            try:
                article_dict = article_to_dict(article)
                processed_articles.append(ArticleResponse(**article_dict))
            except Exception as e:
                print(f"Error processing article: {type(e).__name__}: {str(e)}")
                continue

        return CrawlerResponse(
            articles=processed_articles,
            message=f"Found {len(processed_articles)} article(s)",
        )

    except Exception as e:
        print(f"Error in crawler request: {type(e).__name__}: {str(e)}")
        if isinstance(e, (AttributeError, TypeError)):
            raise HTTPException(
                status_code=422, detail=f"Error processing article data: {str(e)}"
            )
        if isinstance(e, ValueError):
            raise HTTPException(status_code=400, detail=str(e))
        handle_crawler_error(e)


@app.get("/crawl/body", response_model=CrawlerResponse)
async def crawl_body(
    params: CrawlerParams = Depends(),
    include: List[str] = Query(
        ..., description="Required keywords to include in search"
    ),
    sources: Optional[str] = Query(
        None,
        description="Comma-separated list of sources to crawl (e.g., 'TheNewYorker,TheGuardian'). If not specified, uses all sources",
    ),
):
    expanded_include = expand_terms(include)
    print(f"Include terms: {expanded_include}")

    return await handle_crawler_request(
        params,
        expanded_include,
        None,  # exclude parameter is not used for body search
        sources,
        BodyFilterCrawler,
    )


@app.get("/crawl/url", response_model=CrawlerResponse)
async def crawl_url(
    params: CrawlerParams = Depends(),
    include: List[str] = Query(
        ..., description="Required keywords to include in search"
    ),
    exclude: Optional[List[str]] = Query(
        None, description="Optional keywords to exclude from search"
    ),
    sources: Optional[str] = Query(
        None,
        description="Comma-separated list of sources to crawl (e.g., 'TheNewYorker,TheGuardian'). If not specified, uses all sources",
    ),
):
    expanded_include = expand_terms(include)
    expanded_exclude = expand_terms(exclude) if exclude else None
    print(f"Include terms: {expanded_include}")
    if expanded_exclude:
        print(f"Exclude terms: {expanded_exclude}")

    return await handle_crawler_request(
        params,
        expanded_include,
        expanded_exclude,
        sources,
        UrlFilterCrawler,
    )
