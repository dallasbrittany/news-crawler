# news-crawler

<div style="background-color: #fff; border: 1px solid #ddd; padding: 15px; margin: 20px 0; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); transform: rotate(-1deg);">
  <strong>📝 Note:</strong> This project has been an experiment with using Cursor and included some vibe coding as is evident from this note, which I would have never even thought to rotate before.
</div>

Uses `fundus` for news crawling and includes both a CLI mode and an API mode. There are no guarantees with this code, and it could change completely any time. It's a bit of an experiment -- both with news crawling and also with using AI in development (Copilot and Cursor primarily).

If you use this tool, please use it responsibly. Data isn't free, and neither is journalism.

## Usage
- Install with `pipenv` with the Python version specified in `.python-version` -- see bottom of this file for some `pipenv` tips.
- The crawler can be run in two modes: CLI or API. The CLI mode is mainly for quickly experimenting and watching headlines scroll by. The API mode has been added so a UI can be built to connect to it for easier viewing of the articles.
- Right now, there are two types of searches -- body text and URL text. Searching body text allows for searching with multiple keywords using OR. Searching URL text allows for searching for multiple keywords using AND but also allows ensuring there are excluded keywords, as well. There is date filtering available, but it's better supported for the body text search.

When the crawler initializes, it displays the sources grouped by region with counts. For example:
```
Initialized crawler with sources:
US (18): The New York Times, The Washington Post, ...
UK (12): The Guardian, BBC, ...
AU (8): The Sydney Morning Herald, ...
CA (6): The Globe and Mail, ...
```
The numbers in parentheses indicate how many sources are being used from each region. If a source isn't recognized, it will be listed under "Unknown" sources.

### Code Organization

- The `examples` folder contains examples from the `fundus` `README`.
- The `crawlers` folder contains custom search classes.
- `api.py` uses FastAPI for API access.
- `main.py` allows running via CLI or API.
- Tests haven't been added yet (there's a branch where that's a WIP)

### Modes

The API mode has a default timeout of 25 seconds, but the CLI mode has no default timeout. When a timeout occurs in API mode, any articles that were successfully collected up to that point are returned. For CLI mode, articles are printed continuously, and Ctrl+C is a good way to stop the crawler.

For terms containing spaces:
- In CLI mode: Use quotes (`"climate crisis"`)
- In API mode: Use URL encoding (`climate%20crisis`)

### Mock Mode

For testing and development purposes, you can run the crawler in mock mode. This mode uses predefined test data instead of making real network requests, which is useful for the following:
- Offline development and testing
- Faster response times
- Consistent, predictable results
- UI development and integration testing

To use mock mode:

1. CLI Mode with mock data:
```bash
# Search for climate articles using mock data
python main.py cli --crawler body --include climate --mock

# Search URLs with mock data
python main.py cli --crawler url --include tech --exclude AI --mock
```

2. API Mode with mock data:
```bash
# Start the API server in mock mode
python main.py api --mock
```

The mock data includes example articles about:
- Climate change
- Tech regulations
- AI technology
- Healthcare innovation
- Sustainable energy

Mock mode supports all the same filtering options as the real crawler:
- Keyword filtering
- Date filtering
- Source filtering (TheGuardian, TheNewYorker, Wired)
- Article limit

#### Toggling Mock Mode via API

While the API server is running, you can toggle mock mode on and off using the `/mock/{state}` endpoint:

```bash
# Enable mock mode
curl "http://localhost:8000/mock/true"

# Disable mock mode
curl "http://localhost:8000/mock/false"
```

This is useful for:
- Testing both real and mock data in the same session
- Switching between mock and real data without restarting the server
- Integration testing with different data sources

#### CLI Mode Examples

To search for environmental articles from The Guardian in the last 2 days using multiple keywords with OR logic (using many keywords works well for body text search to cover a subject):
```
python main.py cli --crawler body --max_articles 10 --days_back 2 --sources TheGuardian --include pollution environmental "climate crisis" EPA coral reef
```

To search URLs for Apple and technology but exclude the word AI (which might not find many articles, if any):
```
python main.py cli --crawler url --include Apple technology --exclude AI
```

Use a timeout to limit how long the crawler runs and return partial results collected:
```
python main.py cli --crawler body --include climate --timeout 30
```

Required arguments:
- `--include`: List of keywords to include in the search (required)

Optional arguments:
- `--max_articles`: Maximum number of articles to retrieve (default: unlimited).
- `--days_back`: Number of days back to search (default: 7).
- `--exclude`: List of keywords to exclude from URLs (only works with URL crawler, not body search).
- `--timeout`: Maximum number of seconds to run the query (optional, no default timeout). When reached, returns articles collected up to that point.
- `--sources`: List of news sources to crawl (e.g., TheNewYorker, TheGuardian). If not specified, uses all US, UK, Australian, and Canadian sources.

#### API Mode
The crawler can be run as an API server that provides the same functionality as CLI mode but through HTTP endpoints.

```bash
# Start API server with default settings (localhost:8000)
python main.py api

# Start API server with custom host and port
python main.py api --host 0.0.0.0 --port 8080
```

The API documentation will be available at `http://localhost:8000/docs` when the server is running.

Available endpoints:
- `/crawl/body` - Search articles by body content
- `/crawl/url` - Search articles by URL text

Required parameters:
- `include`: Keywords to include in search (required). Can be provided either as multiple parameters or comma-separated values.

Optional parameters:
- `max_articles`: Maximum number of articles to retrieve (optional)
- `days_back`: Days to look back (default: 7)
- `exclude`: Keywords to exclude from URLs (only works with /crawl/url endpoint, not with /crawl/body)
- `timeout`: Maximum number of seconds to run the query (default: 25 seconds). When reached, returns articles collected up to that point.
- `sources`: Comma-separated list of news sources to crawl (e.g., 'TheNewYorker,TheGuardian'). If not specified, uses all US, UK, Australian, and Canadian sources

Example API calls:
```bash
# Search for articles about climate and pollution (uses default 25 second timeout)

# Method 1: Multiple parameters
curl "http://localhost:8000/crawl/body?max_articles=5&include=climate&include=pollution"

# Method 2: Comma-separated (same result as above)
curl "http://localhost:8000/crawl/body?max_articles=5&include=climate,pollution"

# Search for environmental articles with spaces in terms (URL-encoded)
curl "http://localhost:8000/crawl/body?sources=TheGuardian&include=environmental,climate%20crisis,coral%20reef"

# Search for technology articles with a custom timeout and multiple sources
curl "http://localhost:8000/crawl/body?sources=TheNewYorker,TheGuardian&include=technology&timeout=60"

# Search for climate articles from The Guardian, excluding opinion and podcast pieces with URL filtering
curl "http://localhost:8000/crawl/url?sources=TheGuardian&include=climate&exclude=opinion,podcast"
```

For both `include` and `exclude` in API calls, you can provide terms in two ways (at least for now):
1. Multiple parameters: `include=term1&include=term2`
2. Comma-separated: `include=term1,term2`

### Code Formatting
This project uses Black for code formatting. To format your code:

```bash
# Format all Python files in the project
black .

# Format a specific file
black specific_file.py

# Format all Python files in a specific directory
black directory_name/

# Check which files would be reformatted without making changes
black --check .

# Show the changes that would be made without applying them
black --diff .
```

## Future Work
- General code improvements and find anything weird introduced by AI
- Handle this: `Unexpected error processing article: OSError: [Errno 24] Too many open files`
- Handle more than one request at a time in a better way
- Add end_date as option to pass in (and rename days_back to start_date)
- It's matching on part of words (so `threefold` matches `reef`), which isn't helpful in many cases
- Make some more useful preset searches like daily essential news or favorite subjects
- It'd be nice if it saved things rather than just displayed them in the terminal
- Testing that isn't manual
- Sentiment analysis would be really useful
- Making it work properly with news in other languages would be nice
- Improve date filtering when doing URL search
- It'd be nice to be able to simulate the timeout properly with mock data, but that can be done later if it seems useful enough

## Resources
- [fundus](https://github.com/flairNLP/fundus) and [fundus supported publishers](https://github.com/flairNLP/fundus/blob/master/docs/supported_publishers.md)

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
