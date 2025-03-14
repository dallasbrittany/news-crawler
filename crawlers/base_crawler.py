from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
import datetime
import time
import requests
from fundus import Crawler, PublisherCollection, Sitemap, Article
from crawlers.helpers import display, print_divider


class CrawlerError(Exception):
    """Base exception class for crawler errors"""

    pass


class NetworkError(CrawlerError):
    """Raised when network-related issues occur during crawling"""

    pass


class TimeoutError(CrawlerError):
    """Raised when crawler exceeds specified timeout"""

    pass


class BaseCrawler(ABC):
    def __init__(
        self,
        sources,
        max_articles: int,
        days: int,
        timeout_seconds: Optional[int] = None,
    ):
        if days <= 0:
            raise ValueError("days must be greater than 0")
        if max_articles is not None and max_articles <= 0:
            raise ValueError("max_articles must be greater than 0 if specified")
        if timeout_seconds is not None and timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than 0 if specified")

        # NOTE: adding restrict_sources_to=[Sitemap] makes The Guardian not work
        self.crawler = Crawler(*sources)
        self.max_articles = max_articles
        self.days = days
        self.timeout_seconds = timeout_seconds
        self.start_date = datetime.date.today() - datetime.timedelta(days=days)
        # TODO: Allow end date to be passed in instead of assuming it's today

    @abstractmethod
    def get_filter_params(self) -> Dict[str, Any]:
        pass

    def publishing_date_filter(self, extracted: Dict[str, Any]) -> bool:
        end_date = datetime.date.today() - datetime.timedelta(
            days=0
        )  # TODO: allowing a range of dates instead of forcing to end today would be nice
        start_date = end_date - datetime.timedelta(days=self.days)
        if publishing_date := extracted.get("publishing_date"):
            return not (start_date <= publishing_date.date() <= end_date)
        return True

    def run_crawler(self, display_output: bool = True) -> List[Article]:
        filter_params = self.get_filter_params()
        articles = []
        start_time = time.time()
        error_count = 0
        max_retries = 3

        try:
            for article in self.crawler.crawl(
                max_articles=self.max_articles, **filter_params
            ):
                try:
                    # Check if we have a valid publishing date
                    if (
                        not hasattr(article, "publishing_date")
                        or article.publishing_date is None
                    ):
                        if display_output:
                            print("\nSkipping article with no publishing date")
                        continue

                    # URL filters don't check date because they only look at the URLs, so it's done here instead
                    if article.publishing_date.date() >= self.start_date:
                        if display_output:
                            display(article)
                        articles.append(article)
                    elif self.max_articles:
                        if display_output:
                            print("\n(Skipping display of older article.)")
                            print_divider()
                    else:
                        if display_output:
                            print(".")

                    # Check timeout if specified and just stop collecting articles if it's reached
                    elapsed_time = time.time() - start_time
                    if self.timeout_seconds and elapsed_time > self.timeout_seconds:
                        if display_output:
                            print(
                                f"\nTimeout reached after {elapsed_time:.1f} seconds. Returning {len(articles)} articles collected so far."
                            )
                            print_divider()
                        return articles

                except (
                    requests.exceptions.RequestException,
                    requests.exceptions.ConnectionError,
                ) as e:
                    error_count += 1
                    if error_count >= max_retries:
                        raise NetworkError(
                            f"Network error after {max_retries} retries: {str(e)}"
                        )
                    if display_output:
                        print(
                            f"\nNetwork error encountered, retrying ({error_count}/{max_retries})..."
                        )
                    time.sleep(1)  # Add a small delay before retrying
                    continue
                except AttributeError as e:
                    if display_output:
                        print(f"\nSkipping article due to missing attribute: {str(e)}")
                    continue
                except Exception as e:
                    if display_output:
                        print(
                            f"\nUnexpected error processing article: {type(e).__name__}: {str(e)}"
                        )
                    continue

        except Exception as e:
            if display_output:
                print(f"\nError during crawling: {type(e).__name__}: {str(e)}")
                print_divider()
            raise CrawlerError(f"Crawler error: {str(e)}")

        if display_output:
            print(f"\nCrawling completed. Found {len(articles)} articles.")
            print_divider()

        return articles
