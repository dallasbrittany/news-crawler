# from https://github.com/flairNLP/fundus/blob/master/docs/4_how_to_filter_articles.md

from typing import Dict, Any
from fundus import Crawler, PublisherCollection

# only select articles from the past seven days
def date_filter(extracted: Dict[str, Any]) -> bool:
    end_date = datetime.date.today() - datetime.timedelta(weeks=1)
    start_date = end_date - datetime.timedelta(weeks=1)
    if publishing_date := extracted.get("publishing_date"):
        return not (start_date <= publishing_date.date() <= end_date)
    return True

# only select articles which include at least one string from ["pollution", "climate crisis"] in the article body
def body_filter(extracted: Dict[str, Any]) -> bool:
    if body := extracted.get("body"):
        for word in ["pollution", "climate crisis"]:
            if word in str(body).casefold():
                return False
    return True

def topic_filter(extracted: Dict[str, Any]) -> bool:
    if topics := extracted.get("topics"):
        if "usa" in [topic.casefold() for topic in topics]:
            return False
    return True

crawler = Crawler(PublisherCollection.us)
for us_themed_article in crawler.crawl(only_complete=topic_filter):
    print(us_themed_article)
