from fundus import Crawler, PublisherCollection
from fundus.scraping.filter import inverse, regex_filter, lor, land

crawler = Crawler(PublisherCollection.us)

filter1 = regex_filter(
    "advertisement|podcast"
)  # drop all URLs including the strings "advertisement" or "podcast"
filter2 = inverse(
    land(regex_filter("politic"), regex_filter("trump"))
)  # drop all URLs not including the strings "politic" and "trump"

for article in crawler.crawl(max_articles=10, url_filter=lor(filter1, filter2)):
    print(article.html.requested_url)
