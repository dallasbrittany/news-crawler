from fundus import Crawler, PublisherCollection
from fundus.scraping.filter import inverse, regex_filter, lor, land

crawler = Crawler(PublisherCollection.us)

filter_out = regex_filter("advertisement|podcast")
filter_include = inverse(land(regex_filter("coral"), regex_filter("climate")))

# printed in this order so it's easy to scan headlines but scroll up to read more if you want
for article in crawler.crawl(max_articles=10, url_filter=lor(filter_out, filter_include)):
    print(article.authors)
    print(article.body)
    print("\n")
    print(article.title)
    print(article.publishing_date)
    print(article.html.requested_url)
    print("-"*20)
