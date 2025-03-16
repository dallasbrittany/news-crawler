from typing import List, Optional
from datetime import datetime, timedelta
from fundus import Article


def normalize_source_name(name: str) -> str:
    """Normalize source name by removing spaces and special characters."""
    return "".join(name.split())


MOCK_ARTICLES = [
    {
        "title": "Climate Change: A Global Challenge",
        "url": "https://example.com/climate-change",
        "body": "Climate change continues to be a pressing issue. Scientists warn about rising temperatures and their impact on ecosystems. Recent studies show concerning trends in global warming.",
        "source": "The Guardian",
        "publishing_date": datetime.now() - timedelta(days=1),
        "authors": ["Emma Thompson", "James Wilson"],
    },
    {
        "title": "Tech Giants Face New Regulations",
        "url": "https://example.com/tech-regulations",
        "body": "Major technology companies are facing increased scrutiny over data privacy and market dominance. Lawmakers propose new regulations to address concerns.",
        "source": "The New Yorker",
        "publishing_date": datetime.now() - timedelta(days=2),
        "authors": ["Sarah Chen"],
    },
    {
        "title": "Advances in AI Technology",
        "url": "https://example.com/ai-advances",
        "body": "Artificial intelligence continues to evolve with new breakthroughs in machine learning and neural networks. Researchers develop more efficient algorithms.",
        "source": "Wired",
        "publishing_date": datetime.now() - timedelta(days=3),
        "authors": ["Michael Rodriguez", "David Kim", "Lisa Patel"],
    },
    {
        "title": "Healthcare Innovation During Pandemic",
        "url": "https://example.com/healthcare-innovation",
        "body": "The healthcare sector has seen rapid innovation in response to global challenges. Telemedicine and digital health solutions become mainstream.",
        "source": "The Guardian",
        "publishing_date": datetime.now() - timedelta(days=4),
        "authors": ["Dr. Rachel Foster"],
    },
    {
        "title": "Sustainable Energy Solutions",
        "url": "https://example.com/sustainable-energy",
        "body": "Renewable energy adoption continues to grow worldwide. Solar and wind power installations reach record levels as costs decrease.",
        "source": "The New Yorker",
        "publishing_date": datetime.now() - timedelta(days=5),
        "authors": ["Alex Green", "Maria Santos"],
    },
]


class MockArticle:
    def __init__(self, data: dict):
        self._title = data["title"]
        self._url = data["url"]
        self._body = data["body"]
        self._source = data["source"]
        self._publishing_date = data["publishing_date"]
        self._authors = data.get("authors", [])  # Use get() with default empty list
        self.html = type("HTML", (), {"requested_url": data["url"]})()

    @property
    def title(self):
        return self._title

    @property
    def url(self):
        return self._url

    @property
    def body(self):
        return self._body

    @property
    def source(self):
        return self._source

    @property
    def publishing_date(self):
        return self._publishing_date

    @property
    def authors(self):
        return self._authors


def get_mock_articles(
    include_terms: List[str],
    exclude_terms: Optional[List[str]] = None,
    max_articles: Optional[int] = None,
    days_back: int = 7,
    sources: Optional[List[str]] = None,
    is_url_search: bool = False,
) -> List[Article]:
    """
    Filter and return mock articles based on search criteria.
    """
    filtered_articles = []
    cutoff_date = datetime.now() - timedelta(days=days_back)

    print(f"\nMock data searching with terms: {include_terms}")
    print(f"Sources filter: {sources}")
    print(f"Search type: {'URL' if is_url_search else 'Body'}")

    # Normalize source names for comparison
    normalized_sources = (
        [normalize_source_name(s) for s in sources] if sources else None
    )

    for article_data in MOCK_ARTICLES:
        # Skip if article is too old
        if article_data["publishing_date"] < cutoff_date:
            print(f"Skipping article '{article_data['title']}' - too old")
            continue

        # Check source filter
        if sources:
            article_source = normalize_source_name(article_data["source"])
            if article_source not in normalized_sources:
                print(
                    f"Skipping article '{article_data['title']}' - source {article_data['source']} not in {sources}"
                )
                continue

        # Create article instance
        article = MockArticle(article_data)

        # For URL search, check terms in URL
        if is_url_search:
            url_text = article.url.lower()

            # Check include terms
            if not any(term.lower() in url_text for term in include_terms):
                continue

            # Check exclude terms
            if exclude_terms and any(
                term.lower() in url_text for term in exclude_terms
            ):
                continue
        else:
            # For body search, check terms in title and body
            text = (article.title + " " + article.body).lower()

            # Check include terms
            if not any(term.lower() in text for term in include_terms):
                continue

        filtered_articles.append(article)
        print(f"Found matching article: {article.title}")

        if max_articles and len(filtered_articles) >= max_articles:
            break

    return filtered_articles
