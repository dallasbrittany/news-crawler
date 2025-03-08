# news-crawler

Very simple usage of `fundus` for news crawling. If it ends up being helpful, maybe it'll get expanded later.

- The `examples` folder contains examples from the `fundus` `README`.
- The `searches` folder contains custom search classes that can be used from `main.py`.
- `main.py` is where several options for the crawlers are specified like the search terms

## Usage
- Install with `pipenv` and make sure to use Python `3.8+` for `fundus` (note that this repo specifically was built with `3.11.10`)
- To use BodyFilterCrawler, call `python main.py filter`.
- To use UrlFilterCrawler, call `python main.py url`.

## Future Work
- Get the filters to combine better with body filter and date
- Make some more useful preset searches like daily essential news or favorite subjects
- It'd be nice if it saved things rather than just displayed them in the terminal
- It'd be nice to have a UI
- Testing that isn't manual
- Sentiment analysis would be really useful
- Making it work properly with news in other languages would be nice

## Resources
- [fundus](https://github.com/flairNLP/fundus)

> NOTE: Fundus' filters work inversely to Python's built-in filter. A filter in Fundus describes what is filtered out and not what's kept. If a filter returns True on a specific element the element will be dropped.