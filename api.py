from fastapi import FastAPI, Query
from typing import List, Optional
from pydantic import BaseModel
from fundus import PublisherCollection
from crawlers import BodyFilterCrawler, UrlFilterCrawler, SingleSourceCrawler
from crawlers.helpers import print_include_not_implemented, print_exclude_not_implemented

app = FastAPI(
    title="News Crawler API",
    description="API for crawling news articles from various sources",
    version="1.0.0"
)

class CrawlerResponse(BaseModel):
    message: str
    articles: List[dict]

@app.get("/crawl/body", response_model=CrawlerResponse)
async def crawl_body(
    max_articles: Optional[int] = Query(None, description="Maximum number of articles to retrieve"),
    days_back: int = Query(7, description="Number of days back to search"),
    keywords_include: Optional[List[str]] = Query(None, description="Keywords to include in search"),
    keywords_exclude: Optional[List[str]] = Query(None, description="Keywords to exclude from search")
):
    default_sources = (PublisherCollection.us, PublisherCollection.uk)
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
        default_sources, max_articles, days_back, body_search_terms
    )
    articles = crawler.run_crawler()
    
    return CrawlerResponse(
        message=f"Body crawler completed with {len(articles)} articles found",
        articles=articles
    )

@app.get("/crawl/url", response_model=CrawlerResponse)
async def crawl_url(
    max_articles: Optional[int] = Query(None, description="Maximum number of articles to retrieve"),
    days_back: int = Query(7, description="Number of days back to search"),
    keywords_include: Optional[List[str]] = Query(None, description="Required terms in URL"),
    keywords_exclude: Optional[List[str]] = Query(None, description="Terms to filter out from URL")
):
    default_sources = (PublisherCollection.us, PublisherCollection.uk)
    required_terms_default = ["coral", "climate"]
    required_terms = keywords_include if keywords_include else required_terms_default
    
    filter_out_terms_default = ["advertisement", "podcast"]
    filter_out_terms = keywords_exclude if keywords_exclude else filter_out_terms_default
    
    crawler = UrlFilterCrawler(
        default_sources, max_articles, days_back, required_terms, filter_out_terms
    )
    articles = crawler.run_crawler()
    
    return CrawlerResponse(
        message=f"URL crawler completed with {len(articles)} articles found",
        articles=articles
    )

@app.get("/crawl/ny", response_model=CrawlerResponse)
async def crawl_ny(
    max_articles: Optional[int] = Query(None, description="Maximum number of articles to retrieve"),
    days_back: int = Query(7, description="Number of days back to search")
):
    source = PublisherCollection.us.TheNewYorker
    crawler = SingleSourceCrawler([source], max_articles, days_back)
    articles = crawler.run_crawler()
    
    return CrawlerResponse(
        message=f"New Yorker crawler completed with {len(articles)} articles found",
        articles=articles
    )

@app.get("/crawl/guardian", response_model=CrawlerResponse)
async def crawl_guardian(
    max_articles: Optional[int] = Query(None, description="Maximum number of articles to retrieve"),
    days_back: int = Query(7, description="Number of days back to search")
):
    source = PublisherCollection.uk.TheGuardian
    crawler = SingleSourceCrawler([source], max_articles, days_back)
    articles = crawler.run_crawler()
    
    return CrawlerResponse(
        message=f"Guardian crawler completed with {len(articles)} articles found",
        articles=articles
    ) 