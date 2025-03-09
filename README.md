# news-crawler

Very simple usage of `fundus` for news crawling. If it ends up being helpful, maybe it'll get expanded later.

- The `examples` folder contains examples from the `fundus` `README`.
- The `crawlers` folder contains custom search classes that can be used from `main.py`.
- `main.py` is where several options for the crawlers are specified like the search terms and where the custom search classes are called

## Usage
- Install with `pipenv` and make sure to use Python `3.8+` for `fundus` (note that this repo specifically was built with `3.11.10`) -- see bottom of this file for some tips
- To use see usage, call run `main.py` and see something like this:
```
usage: main.py [-h] [--max_articles MAX_ARTICLES] [--days_back DAYS_BACK] [--include INCLUDE [INCLUDE ...]]
               [--exclude EXCLUDE [EXCLUDE ...]]
               {body,url,ny,guardian}
```

- For example, to see 10 articles from the Guardian that are from the last 2 days:
```
python main.py guardian --max_articles 10 --days_back 2
```

Or to specify your own search terms for the body of articles in US and UK news sources with defaults for max articles and days back:

```
python main.py body --include AI technology
```

Or to specify technology but not AI in the URL (with the rest of the settings being defaults):

```
python main.py url --include technology --exclude AI
```

## Future Work
- Add API support
- Add end_date as option to pass in (and rename days_back to start_date)
- Confirm if the example provided for date filter is actually wrong and if so open a PR in their repo
- Allow passing in the sources instead of ever hard-coding them
- More options for search (like filtering with a single source)
- Handle errors gracefully like `lxml.etree.ParserError: Document is empty`
- It's matching on part of words (so `threefold` matches `reef`), which isn't helpful in many cases
- Make some more useful preset searches like daily essential news or favorite subjects
- It'd be nice if it saved things rather than just displayed them in the terminal
- It'd be nice to have a UI
- Testing that isn't manual
- Sentiment analysis would be really useful
- Making it work properly with news in other languages would be nice
- Improve date filtering when doing URL search
- General code improvements

## Resources
- [fundus](https://github.com/flairNLP/fundus)

> NOTE: Fundus' filters work inversely to Python's built-in filter. A filter in Fundus describes what is filtered out and not what's kept. If a filter returns True on a specific element the element will be dropped.

### Python

Before running, get the virtual environment ready:
```
pipenv --python $(pyenv which python)
pipenv shell
pipenv install
```

To remove the virtual environment:
```
pipenv --rm
```