from fastapi import FastAPI, Query, HTTPException, Depends
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, field_validator, Field
import datetime
from fundus import PublisherCollection, Article
from crawlers import BodyFilterCrawler, UrlFilterCrawler
from crawlers.base_crawler import CrawlerError, NetworkError, TimeoutError
from crawlers.helpers import (
    print_include_not_implemented,
    print_exclude_not_implemented,
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
        return (
            PublisherCollection.us,
            PublisherCollection.uk,
            PublisherCollection.au,
            PublisherCollection.ca,
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
    return (
        tuple(sources)
        if sources
        else (
            PublisherCollection.us,
            PublisherCollection.uk,
            PublisherCollection.au,
            PublisherCollection.ca,
        )
    )


@app.get("/crawl/body", response_model=CrawlerResponse)
async def crawl_body(
    params: CrawlerParams = Depends(),
    keywords_include: Optional[List[str]] = Query(
        None, description="Keywords to include in search"
    ),
    keywords_exclude: Optional[List[str]] = Query(
        None, description="Keywords to exclude from search"
    ),
):
    try:
        sources = get_sources(params.sources)
        terms_default = [
            "pollution",
            "environmental",
            "climate crisis",
            "EPA",
            "coral",
            "reef",
        ]
        body_search_terms = keywords_include if keywords_include else terms_default

        crawler = BodyFilterCrawler(
            sources,
            params.max_articles,
            params.days_back,
            body_search_terms,
            timeout_seconds=params.timeout,
        )
        articles = crawler.run_crawler(
            display_output=True
        )  # Enable display output temporarily for debugging
        print(f"Crawler returned {len(articles)} articles")

        processed_articles = []
        for i, article in enumerate(articles):
            try:
                processed_article = article_to_dict(article)
                processed_articles.append(processed_article)
            except Exception as e:
                print(f"Error processing article {i}: {type(e).__name__}: {str(e)}")
                continue

        return CrawlerResponse(
            message=f"Body crawler completed with {len(processed_articles)} articles found",
            articles=processed_articles,
        )
    except Exception as e:
        print(f"Error in crawl_body: {type(e).__name__}: {str(e)}")
        if isinstance(e, (AttributeError, TypeError)):
            raise HTTPException(
                status_code=422, detail=f"Error processing article data: {str(e)}"
            )
        if isinstance(e, ValueError):
            raise HTTPException(status_code=400, detail=str(e))
        return handle_crawler_error(e)


@app.get("/crawl/url", response_model=CrawlerResponse)
async def crawl_url(
    params: CrawlerParams = Depends(),
    keywords_include: Optional[List[str]] = Query(
        None, description="Required terms in URL"
    ),
    keywords_exclude: Optional[List[str]] = Query(
        None, description="Terms to filter out from URL"
    ),
):
    try:
        sources = get_sources(params.sources)
        required_terms_default = ["coral", "climate"]
        required_terms = (
            keywords_include if keywords_include else required_terms_default
        )

        filter_out_terms_default = ["advertisement", "podcast"]
        filter_out_terms = (
            keywords_exclude if keywords_exclude else filter_out_terms_default
        )

        crawler = UrlFilterCrawler(
            sources,
            params.max_articles,
            params.days_back,
            required_terms,
            filter_out_terms,
            timeout_seconds=params.timeout,
        )
        articles = crawler.run_crawler(display_output=False)

        return CrawlerResponse(
            message=f"URL crawler completed with {len(articles)} articles found",
            articles=[article_to_dict(article) for article in articles],
        )
    except Exception as e:
        return handle_crawler_error(e)
