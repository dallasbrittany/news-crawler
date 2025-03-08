# news-crawler

Very simple usage of `fundus` for news crawling. If it ends up being helpful, maybe it'll get expanded later.

- The `examples` folder contains examples from the `fundus` `README`.
- The `searches` folder contains custom search classes that can be used from `main.py`.
- `main.py` is where several options for the crawlers are specified like the search terms

### Usage
- Install with `pipenv` and make sure to use Python `3.8+` for `fundus` (note that this repo specifically was built with `3.11.10`)
- To use BodyFilterCrawler, call `python main.py filter`.
- To use UrlFilterCrawler, call `python main.py url`.

## Resources
- [fundus](https://github.com/flairNLP/fundus)

> NOTE: Fundus' filters work inversely to Python's built-in filter. A filter in Fundus describes what is filtered out and not what's kept. If a filter returns True on a specific element the element will be dropped.