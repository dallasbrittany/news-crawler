# From the fundus README

from fundus import PublisherCollection, Crawler

# initialize the crawler for The New Yorker
crawler = Crawler(PublisherCollection.us.TheNewYorker)

# crawl 2 articles and print
for article in crawler.crawl(max_articles=2):
    print(article)
