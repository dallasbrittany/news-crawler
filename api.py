from fastapi import FastAPI, Query, HTTPException, Depends
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, field_validator, Field
import datetime
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
    publishing_date: str
    body: str
    authors: List[str]


class CrawlerResponse(BaseModel):
    message: str
    articles: List[ArticleResponse]
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
    try:
        return {
            "title": article.title or "",
            "url": article.html.requested_url,
            "publishing_date": str(article.publishing_date),
            "body": str(article.body),
            "authors": article.authors or [],
        }
    except AttributeError as e:
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


async def handle_crawler_request(
    params: CrawlerParams,
    keywords_include: Optional[List[str]],
    keywords_exclude: Optional[List[str]],
    sources: Optional[str],
    crawler_class,
    default_include_terms: List[str],
    default_exclude_terms: Optional[List[str]] = None,
) -> CrawlerResponse:
    """Handle common crawler request logic for both body and URL endpoints."""
    try:
        print(f"API received timeout parameter: {params.timeout} seconds")

        # Parse and validate sources
        sources_list = parse_sources(sources, params.sources)
        sources = get_sources(sources_list)

        # Set up search terms
        include_terms = keywords_include if keywords_include else default_include_terms
        exclude_terms = (
            keywords_exclude if keywords_exclude else (default_exclude_terms or [])
        )

        print(f"Creating crawler with timeout: {params.timeout} seconds")
        if crawler_class == UrlFilterCrawler:
            crawler = crawler_class(
                sources,
                params.max_articles,
                params.days_back,
                include_terms,
                exclude_terms,
                timeout_seconds=params.timeout,
            )
        else:  # BodyFilterCrawler
            crawler = crawler_class(
                sources,
                params.max_articles,
                params.days_back,
                include_terms,
                timeout_seconds=params.timeout,
            )

        # Run crawler with appropriate display settings
        display_output = (
            crawler_class == BodyFilterCrawler
        )  # Only show output for body crawler
        articles = crawler.run_crawler(
            display_output=display_output,
            show_body=False,  # Don't show article bodies in API mode
        )
        print(f"Crawler returned {len(articles)} articles")

        # Process articles
        processed_articles = []
        for i, article in enumerate(articles):
            try:
                processed_article = article_to_dict(article)
                processed_articles.append(processed_article)
            except Exception as e:
                print(f"Error processing article {i}: {type(e).__name__}: {str(e)}")
                continue

        return CrawlerResponse(
            message=f"{crawler_class.__name__} completed with {len(processed_articles)} article(s) found",
            articles=processed_articles,
        )

    except Exception as e:
        print(f"Error in crawler request: {type(e).__name__}: {str(e)}")
        if isinstance(e, (AttributeError, TypeError)):
            raise HTTPException(
                status_code=422, detail=f"Error processing article data: {str(e)}"
            )
        if isinstance(e, ValueError):
            raise HTTPException(status_code=400, detail=str(e))
        return handle_crawler_error(e)


@app.get("/crawl/body", response_model=CrawlerResponse)
async def crawl_body(
    params: CrawlerParams = Depends(),
    keywords_include: Optional[List[str]] = Query(
        None, description="Keywords to include in search"
    ),
    keywords_exclude: Optional[List[str]] = Query(
        None, description="Keywords to exclude from search"
    ),
    sources: Optional[str] = Query(
        None,
        description="Comma-separated list of sources to crawl (e.g., 'TheNewYorker,TheGuardian'). If not specified, uses all sources",
    ),
):
    default_terms = [
        "pollution",
        "environmental",
        "climate crisis",
        "EPA",
        "coral",
        "reef",
    ]
    return await handle_crawler_request(
        params,
        keywords_include,
        keywords_exclude,
        sources,
        BodyFilterCrawler,
        default_terms,
    )


@app.get("/crawl/url", response_model=CrawlerResponse)
async def crawl_url(
    params: CrawlerParams = Depends(),
    keywords_include: Optional[List[str]] = Query(
        None, description="Required terms in URL"
    ),
    keywords_exclude: Optional[List[str]] = Query(
        None, description="Terms to filter out from URL"
    ),
    sources: Optional[str] = Query(
        None,
        description="Comma-separated list of sources to crawl (e.g., 'TheNewYorker,TheGuardian'). If not specified, uses all sources",
    ),
):
    return await handle_crawler_request(
        params,
        keywords_include,
        keywords_exclude,
        sources,
        UrlFilterCrawler,
        ["coral", "climate"],
        ["advertisement", "podcast"],
    )
