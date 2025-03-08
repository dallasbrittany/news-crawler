from fundus import PublisherCollection, Crawler, Sitemap

# modified from fundus README

MAX_ARTICLES=10

# initialize a crawler for us/uk based publishers and restrict to Sitemaps only
crawler = Crawler(PublisherCollection.us, PublisherCollection.uk, restrict_sources_to=[Sitemap])

# crawl specified number of articles and print
for article in crawler.crawl(max_articles=MAX_ARTICLES):
  print(article)
