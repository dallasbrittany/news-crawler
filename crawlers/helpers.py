# Warnings


def print_include_not_implemented():
    print(
        "Provided included keywords will be ignored, as that feature is not implemented yet for this type of search.\n"
    )


def print_exclude_not_implemented():
    print(
        "Provided excluded keywords will be ignored, as that feature is not implemented yet for this type of search.\n"
    )


def print_divider():
    print("-" * 20)


# The following are simple ways to display the article so it is easy to see a summary but also go back and read the entire body when needed


def display(article, show_body=True):
    """
    Format:

    [article body] (if show_body=True)

    [article title]
    [date like 2025-03-08 07:00:00-05:00]
    [url]
    """
    print(article.authors)
    if show_body:
        print(article.body)
    print("\n")
    print(article.title)
    print(article.publishing_date)
    print(article.html.requested_url)
    print_divider()


def display_alt(article, show_body=True):
    """
    Format:

    [body] (if show_body=True)
    Fundus-Article including [number] image(s):
    - Title: [title]
    - Text:  [beginning of the body]
    - URL:   [url]
    - From:  [source name with date formatted like (2025-03-08 15:30)]
    """
    if show_body:
        print(article.body)
        print("\n")
    print(article)
    print_divider()
