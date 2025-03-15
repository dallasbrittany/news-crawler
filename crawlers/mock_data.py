from typing import List, Optional
from datetime import datetime, timedelta
from fundus import Article

MOCK_ARTICLES = [
    {
        "title": "Climate Change: A Global Challenge",
        "url": "https://example.com/climate-change",
        "body": "Climate change continues to be a pressing issue. Scientists warn about rising temperatures and their impact on ecosystems. Recent studies show concerning trends in global warming.",
        "source": "TheGuardian",
        "publishing_date": datetime.now() - timedelta(days=1),
    },
    {
        "title": "Tech Giants Face New Regulations",
        "url": "https://example.com/tech-regulations",
        "body": "Major technology companies are facing increased scrutiny over data privacy and market dominance. Lawmakers propose new regulations to address concerns. Will it do any good? Who knows. Time will tell.",
        "source": "TheNewYorker",
        "publishing_date": datetime.now() - timedelta(days=2),
    },
    {
        "title": "Advances in AI Technology",
        "url": "https://example.com/ai-advances",
        "body": "Artificial intelligence continues to evolve with new breakthroughs in machine learning and neural networks. Researchers develop more efficient algorithms.",
        "source": "Wired",
        "publishing_date": datetime.now() - timedelta(days=3),
    },
    {
        "title": "Healthcare Innovation During Pandemic",
        "url": "https://example.com/healthcare-innovation",
        "body": "The healthcare sector has seen rapid innovation in response to global challenges. Telemedicine and digital health solutions become mainstream.",
        "source": "TheGuardian",
        "publishing_date": datetime.now() - timedelta(days=4),
    },
    {
        "title": "Sustainable Energy Solutions",
        "url": "https://example.com/sustainable-energy",
        "body": "Renewable energy adoption continues to grow worldwide. Solar and wind power installations reach record levels as costs decrease.",
        "source": "TheNewYorker",
        "publishing_date": datetime.now() - timedelta(days=5),
    },
]


class MockArticle:
    def __init__(self, data: dict):
        self._title = data["title"]
        self._url = data["url"]
        self._body = data["body"]
        self._source = data["source"]
        self._publishing_date = data["publishing_date"]
        self._authors = []
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
) -> List[Article]:
    """
    Filter and return mock articles based on search criteria.
    """
    filtered_articles = []
    cutoff_date = datetime.now() - timedelta(days=days_back)

    print(f"Mock data searching with terms: {include_terms}")
    print(f"Sources filter: {sources}")

    for article_data in MOCK_ARTICLES:
        # Filter by date
        if article_data["publishing_date"] < cutoff_date:
            continue

        # Filter by source if specified
        if sources and article_data["source"] not in sources:
            continue

        # Check include terms (any term must match)
        article_text = f"{article_data['title']} {article_data['body']}".lower()
        if not any(term.lower() in article_text for term in include_terms):
            continue

        # Check exclude terms if specified
        if exclude_terms and any(
            term.lower() in article_text for term in exclude_terms
        ):
            continue

        filtered_articles.append(MockArticle(article_data))

    # Apply max_articles limit if specified
    if max_articles is not None:
        filtered_articles = filtered_articles[:max_articles]

    print(f"Mock data found {len(filtered_articles)} matching articles")
    return filtered_articles
