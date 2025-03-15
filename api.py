from fastapi import FastAPI, Query, HTTPException, Depends
from fastapi.concurrency import run_in_threadpool
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, field_validator, Field
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
    publishing_date: Any  # Changed from str to Any to handle datetime
    body: str
    authors: Optional[List[str]] = []  # Made optional with default empty list


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
        valid_sources = {
            **vars(PublisherCollection.us),
            **vars(PublisherCollection.uk),
            **vars(PublisherCollection.au),
            **vars(PublisherCollection.ca),
        }
        for source in v:
            if source not in valid_sources:
                raise ValueError(
                    f"Invalid source: {source}. Valid sources are: {', '.join(valid_sources.keys())}"
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
        return {
            "title": article.title,
            "url": (
                article.url if hasattr(article, "url") else article.html.requested_url
            ),
            "publishing_date": article.publishing_date,
            "body": article.body,
            "authors": getattr(article, "authors", []),
        }
    except AttributeError as e:
        print(f"Error processing article: {str(e)}")
        raise HTTPException(
            status_code=422, detail=f"Error processing article data: {str(e)}"
        )


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
    for name in source_names:
        found = False
        for collection in PUBLISHER_COLLECTIONS.values():
            if hasattr(collection, name):
                sources.append(getattr(collection, name))
                print(f"Found {name} in {collection.__class__.__name__}")
                found = True
                break
        if not found:
            invalid_sources.append(name)
            print(f"Source not found: {name}")

    if invalid_sources:
        valid_sources = {}
        for collection in PUBLISHER_COLLECTIONS.values():
            valid_sources.update(
                {
                    name: source
                    for name, source in vars(collection).items()
                    if not name.startswith("__")
                }
            )
        valid_source_names = sorted(valid_sources.keys())
        raise ValueError(
            f"Invalid source(s): {', '.join(invalid_sources)}. "
            f"Valid sources are: {', '.join(valid_source_names)}"
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
