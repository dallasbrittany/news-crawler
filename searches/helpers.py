# These are simple ways to display the article so it is easy to see a summary but also go back and read the entire body when needed

def display1(article):
    """
    Format:

    [article body]

    [article title]
    [date like 2025-03-08 07:00:00-05:00]
    [url]
    """
    print(article.authors)
    print(article.body)
    print("\n")
    print(article.title)
    print(article.publishing_date)
    print(article.html.requested_url)
    print("-"*20)

def display2(article):
    """
    Format:

    [body]
    Fundus-Article including [number] image(s):
    - Title: [title]
    - Text:  [beginning of the body]
    - URL:   [url]
    - From:  [source name with date formatted like (2025-03-08 15:30)]
    """
    print(article.body)
    print("\n")
    print(article)
    print("-"*20)