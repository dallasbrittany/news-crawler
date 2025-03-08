from typing import Dict, Any
from fundus import Crawler, PublisherCollection
from fundus.scraping.filter import inverse, land, lor
import datetime
from helpers import display1, display2

BODY_SEARCH_TERMS = ["pollution", "climate crisis", "environmental"]
DAYS = 1

END_DATE = datetime.date.today() - datetime.timedelta(days=DAYS)

CRAWLER = Crawler(PublisherCollection.us)

def body_filter(extracted: Dict[str, Any]) -> bool:
    if body := extracted.get("body"):
        for word in BODY_SEARCH_TERMS:
            if word in str(body).casefold():
                return False
    return True

for article in CRAWLER.crawl(only_complete=body_filter):
    # land(body_filter, date_filter) doesn't seem to work as expected, so just not printing the ones with unwanted dates is a workaround
    if article.publishing_date.date() > END_DATE:
        display1(article)
