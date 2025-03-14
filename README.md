# news-crawler

Very simple usage of `fundus` for news crawling. If it ends up being helpful, maybe it'll get expanded later.

- The `examples` folder contains examples from the `fundus` `README`.
- The `crawlers` folder contains custom search classes that can be used from `main.py`.
- `main.py` is where several options for the crawlers are specified like the search terms and where the custom search classes are called

## Usage
- Install with `pipenv` and make sure to use Python `3.8+` for `fundus` (note that this repo specifically was built with `3.11.10`) -- see bottom of this file for some tips
- The crawler can be run in two modes: CLI or API. To see usage, run `main.py` and see something like this:
```
usage: main.py [-h] {cli,api} [--crawler {body,url,ny,guardian}] [--max_articles MAX_ARTICLES]
               [--days_back DAYS_BACK] [--include INCLUDE [INCLUDE ...]]
               [--exclude EXCLUDE [EXCLUDE ...]] [--timeout TIMEOUT] [--host HOST] [--port PORT]
```

### CLI Mode
For example, to see 10 articles from the Guardian that are from the last 2 days:
```
python main.py cli --crawler guardian --max_articles 10 --days_back 2
```

Or to specify your own search terms for the body of articles in US and UK news sources with defaults for max articles and days back:

```
python main.py cli --crawler body --include AI technology
```

Or to specify technology but not AI in the URL (with the rest of the settings being defaults):

```
python main.py cli --crawler url --include technology --exclude AI
```

You can also set a timeout to limit how long the crawler runs:
```
python main.py cli --crawler body --include climate --timeout 30  # Stop after 30 seconds
```

Optional arguments:
- `--max_articles`: Maximum number of articles to retrieve (default: unlimited)
- `--days_back`: Number of days back to search (default: 7)
- `--include`: List of keywords to include in the search
- `--exclude`: List of keywords to exclude from the search
- `--timeout`: Maximum number of seconds to run the query (default: no timeout)

### API Mode
The crawler can also be run as an API server that provides the same functionality through HTTP endpoints:

```bash
# Start API server with default settings (localhost:8000)
python main.py api

# Start API server with custom host and port
python main.py api --host 0.0.0.0 --port 8080
```

The API documentation will be available at `http://localhost:8000/docs` when the server is running.

Available endpoints:
- `/crawl/body` - Search articles by body content
- `/crawl/url` - Search articles by URL patterns
- `/crawl/ny` - Get articles from The New Yorker
- `/crawl/guardian` - Get articles from The Guardian

Each endpoint supports the following query parameters:
- `max_articles`: Maximum number of articles to retrieve (optional)
- `days_back`: Days to look back (default: 7)
- `keywords_include`: Keywords to include in search (for body and URL endpoints)
- `keywords_exclude`: Keywords to exclude from search (for body and URL endpoints)
- `timeout`: Maximum number of seconds to run the query (optional)

Example API calls:
```bash
# Get articles with specific keywords in body, timeout after 30 seconds
curl "http://localhost:8000/crawl/body?max_articles=5&keywords_include=climate&keywords_include=pollution&timeout=30"

# Get articles with specific URL patterns, timeout after 1 minute
curl "http://localhost:8000/crawl/url?max_articles=10&keywords_include=technology&keywords_exclude=AI&timeout=60"

# Get articles from The New Yorker with a 45 second timeout
curl "http://localhost:8000/crawl/ny?max_articles=5&timeout=45"
```

## Future Work
- Add end_date as option to pass in (and rename days_back to start_date)
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