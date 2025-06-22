from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
import datetime
import time
import threading
import requests
import signal
from fundus import Crawler, PublisherCollection, Sitemap, Article
from crawlers.helpers import display, print_divider
from crawlers.mock_data import normalize_source_name


def timeout_handler(timeout_event):
    timeout_event.set()


def cli_timeout_handler(signum, frame):
    raise TimeoutError("Crawler operation timed out")


class CrawlerError(Exception):
    """Base exception class for crawler errors"""

    pass


class NetworkError(CrawlerError):
    """Raised when network-related issues occur during crawling"""

    pass


class TimeoutError(Exception):
    """Raised when crawler exceeds specified timeout"""

    pass


# Constants for publisher collections
PUBLISHER_COLLECTIONS = {
    "US": PublisherCollection.us,
    "UK": PublisherCollection.uk,
    "AU": PublisherCollection.au,
    "CA": PublisherCollection.ca,
}

PUBLISHER_COLLECTIONS_LIST = list(PUBLISHER_COLLECTIONS.values())


def format_sources(sources_list):
    """Format sources list in a readable way, grouped by region."""
    # Initialize source lists for each region
    sources_by_region = {region: [] for region in PUBLISHER_COLLECTIONS}
    unknown_sources = []

    for source in sources_list:
        # Handle collection objects
        if isinstance(source, type(PublisherCollection.us)):
            # Extract all publishers from the collection
            for name, publisher in vars(source).items():
                if not name.startswith("__") and hasattr(publisher, "name"):
                    # Find which collection this publisher belongs to
                    for region, collection in PUBLISHER_COLLECTIONS.items():
                        if source == collection:
                            sources_by_region[region].append(publisher.name)
                            break
            continue

        # Handle individual publisher objects
        source_name = getattr(source, "name", None)
        if source_name:
            # Check which collection it belongs to by comparing the actual source object
            found = False
            for region, collection in PUBLISHER_COLLECTIONS.items():
                for class_name, publisher in vars(collection).items():
                    if not class_name.startswith("__") and publisher == source:
                        sources_by_region[region].append(source_name)
                        found = True
                        break
                if found:
                    break
            if not found:
                unknown_sources.append(source_name)
        else:
            print(
                f"DEBUG: Source has no name attribute and is not a collection, using str: {str(source)}"
            )
            unknown_sources.append(str(source))

    # Build output string
    output = []
    for region, sources in sources_by_region.items():
        if sources:
            output.append(f"{region} ({len(sources)}): {', '.join(sorted(sources))}")
    if unknown_sources:
        output.append(
            f"Unknown ({len(unknown_sources)}): {', '.join(sorted(unknown_sources))}"
        )

    if not output:
        output.append("No sources found!")

    return "\n".join(output)


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

        # Convert sources to a list if it's a single source
        sources_list = (
            [sources] if not isinstance(sources, (list, tuple)) else list(sources)
        )
        print("\nProcessing crawler initialization...")
        # print(f"Source input type: {type(sources)}")
        formatted_sources = format_sources(sources_list)
        if formatted_sources:
            print("\nInitialized crawler with sources:")
            print(formatted_sources)
        else:
            print("\nWARNING: No valid sources found during initialization")

        # NOTE: adding restrict_sources_to=[Sitemap] makes The Guardian not work
        self.crawler = Crawler(sources_list)

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

    def run_crawler(
        self, display_output: bool = True, show_body: bool = True
    ) -> List[Article]:
        filter_params = self.get_filter_params()
        articles = []
        start_time = time.time()
        error_count = 0
        max_retries = 3

        # Set up the timeout handler
        timer = None
        timeout_event = threading.Event()
        if self.timeout_seconds:
            timer = threading.Timer(
                self.timeout_seconds, timeout_handler, args=(timeout_event,)
            )
            timer.start()
            print(f"Set crawler timeout for {self.timeout_seconds} seconds")

        try:
            article_iterator = self.crawler.crawl(
                max_articles=self.max_articles, **filter_params
            )

            while True:
                # Check for timeout
                if timeout_event.is_set():
                    raise TimeoutError("Crawler operation timed out")

                try:
                    # Check for timeout again before fetching next article
                    if timeout_event.is_set():
                        raise TimeoutError("Crawler operation timed out")

                    article = next(article_iterator, None)
                    if article is None:  # No more articles
                        break

                    # Check for timeout after fetching article
                    if timeout_event.is_set():
                        raise TimeoutError("Crawler operation timed out")

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
                            display(article, show_body=show_body)
                        articles.append(article)
                    elif self.max_articles:
                        if display_output:
                            print("\n(Skipping display of older article.)")
                            print_divider()
                    else:
                        if display_output:
                            print(".")

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
                except TimeoutError as e:
                    if str(e) == "Crawler operation timed out":
                        # This is our intentional timeout, handle it gracefully
                        elapsed_time = time.time() - start_time
                        if display_output:
                            print(
                                f"\nTimeout reached after {elapsed_time:.1f} seconds (limit was {self.timeout_seconds} seconds). Returning {len(articles)} articles collected so far."
                            )
                            print_divider()
                        return articles
                    else:
                        # This is an unexpected timeout error
                        if display_output:
                            print(f"\nUnexpected timeout error: {str(e)}")
                        raise
                except Exception as e:
                    if display_output:
                        print(
                            f"\nUnexpected error processing article: {type(e).__name__}: {str(e)}"
                        )
                    continue

        except TimeoutError as e:
            if str(e) == "Crawler operation timed out":
                # This is our intentional timeout, handle it gracefully
                elapsed_time = time.time() - start_time
                if display_output:
                    print(
                        f"\nTimeout reached after {elapsed_time:.1f} seconds (limit was {self.timeout_seconds} seconds). Returning {len(articles)} articles collected so far."
                    )
                    print_divider()
                return articles
            else:
                # This is an unexpected timeout error
                if display_output:
                    print(f"\nUnexpected timeout error: {str(e)}")
                raise

        except Exception as e:
            if display_output:
                print(f"\nError during crawling: {type(e).__name__}: {str(e)}")
                print_divider()
            raise CrawlerError(f"Crawler error: {str(e)}")

        finally:
            if timer:
                timer.cancel()  # Cancel the timer if it's still running

        if display_output:
            print(f"\nCrawling completed. Found {len(articles)} article(s).")
            print_divider()

        return articles


class CLICrawler(BaseCrawler):
    """A version of BaseCrawler that uses signal-based timeouts for CLI mode."""

    def run_crawler(
        self, display_output: bool = True, show_body: bool = True
    ) -> List[Article]:
        filter_params = self.get_filter_params()
        articles = []
        start_time = time.time()
        error_count = 0
        max_retries = 3

        # Set up the timeout handler using signal
        original_handler = None
        if self.timeout_seconds:
            original_handler = signal.signal(signal.SIGALRM, cli_timeout_handler)
            signal.alarm(self.timeout_seconds)
            print(f"Set crawler timeout for {self.timeout_seconds} seconds")

        try:
            article_iterator = self.crawler.crawl(
                max_articles=self.max_articles, **filter_params
            )

            while True:
                try:
                    article = next(article_iterator, None)
                    if article is None:  # No more articles
                        break

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
                            display(article, show_body=show_body)
                        articles.append(article)
                    elif self.max_articles:
                        if display_output:
                            print("\n(Skipping display of older article.)")
                            print_divider()
                    else:
                        if display_output:
                            print(".")

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
                except TimeoutError as e:
                    # This is our intentional timeout, handle it gracefully
                    elapsed_time = time.time() - start_time
                    if display_output:
                        print(
                            f"\nTimeout reached after {elapsed_time:.1f} seconds (limit was {self.timeout_seconds} seconds). Returning {len(articles)} articles collected so far."
                        )
                        print_divider()
                    return articles
                except Exception as e:
                    if display_output:
                        print(
                            f"\nUnexpected error processing article: {type(e).__name__}: {str(e)}"
                        )
                    continue

        except TimeoutError as e:
            # This is our intentional timeout, handle it gracefully
            elapsed_time = time.time() - start_time
            if display_output:
                print(
                    f"\nTimeout reached after {elapsed_time:.1f} seconds (limit was {self.timeout_seconds} seconds). Returning {len(articles)} articles collected so far."
                )
                print_divider()
            return articles
        except Exception as e:
            if display_output:
                print(f"\nError during crawling: {type(e).__name__}: {str(e)}")
                print_divider()
            raise CrawlerError(f"Crawler error: {str(e)}")
        finally:
            # Restore the original signal handler and cancel any pending alarm
            if original_handler:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, original_handler)

        if display_output:
            print(f"\nCrawling completed. Found {len(articles)} article(s).")
            print_divider()

        return articles
