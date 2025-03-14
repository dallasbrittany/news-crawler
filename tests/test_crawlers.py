"""Tests for the crawler classes."""

import unittest
from unittest.mock import patch, MagicMock, call
from datetime import datetime, date
import signal
from crawlers.base_crawler import BaseCrawler
from crawlers.body_filter import BodyFilterCrawler
from crawlers.url_filter import UrlFilterCrawler


class TestBaseCrawler(unittest.TestCase):
    """Test cases for the BaseCrawler class."""

    @patch('signal.alarm')
    @patch('time.time')
    @patch('time.sleep')
    def setUp(self, mock_sleep, mock_time, mock_alarm):
        """Set up test fixtures."""
        self.mock_sleep = mock_sleep
        self.mock_time = mock_time
        self.mock_alarm = mock_alarm
        self.mock_time.return_value = 0  # Start time
        self.crawler = BaseCrawler(timeout_seconds=10)

    def tearDown(self):
        """Clean up after each test."""
        # Ensure alarm is disabled after each test
        signal.alarm(0)

    @patch('signal.alarm')
    @patch('time.time')
    def test_timeout_handling(self, mock_time, mock_alarm):
        """Test that the crawler handles timeouts correctly."""
        mock_time.side_effect = [0, 5, 11]  # Start, middle, exceed timeout
        
        def raise_timeout(*args):
            raise TimeoutError("Test timeout")
        
        # Simulate a timeout by triggering the signal handler
        with patch('signal.signal') as mock_signal:
            mock_signal.side_effect = raise_timeout
            articles = self.crawler.run_crawler()
            
            # Verify timeout was set and cleared
            mock_alarm.assert_has_calls([
                call(10),  # Set timeout
                call(0)   # Clear timeout
            ])
            
            self.assertEqual(articles, [])


class TestBodyFilterCrawler(unittest.TestCase):
    """Test cases for the BodyFilterCrawler class."""

    def setUp(self):
        """Set up test fixtures."""
        self.crawler = BodyFilterCrawler(
            search_terms=["test"],
            timeout_seconds=10
        )

    @patch('fundus.Article')
    def test_body_filtering(self, mock_article):
        """Test that articles are filtered based on body content."""
        # Create mock articles
        mock_articles = [
            MagicMock(
                title="Test Article 1",
                body="This is a test article",
                html=MagicMock(requested_url="http://example.com/1"),
                publishing_date=date.today(),
                authors=["Author 1"]
            ),
            MagicMock(
                title="Test Article 2",
                body="This article doesn't match",
                html=MagicMock(requested_url="http://example.com/2"),
                publishing_date=date.today(),
                authors=["Author 2"]
            )
        ]
        
        # Configure mock to return our test articles
        mock_article.objects.filter.return_value = mock_articles
        
        # Run crawler with search terms
        articles = self.crawler.run_crawler()
        
        # Verify filtering
        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0]["title"], "Test Article 1")

    def test_empty_search_terms(self):
        """Test that empty search terms are handled correctly."""
        with self.assertRaises(ValueError):
            BodyFilterCrawler(search_terms=[], timeout_seconds=10)


class TestUrlFilterCrawler(unittest.TestCase):
    """Test cases for the UrlFilterCrawler class."""

    def setUp(self):
        """Set up test fixtures."""
        self.crawler = UrlFilterCrawler(
            filter_include_terms=["news"],
            filter_out_terms=["opinion"],
            timeout_seconds=10
        )

    @patch('fundus.Article')
    def test_url_filtering(self, mock_article):
        """Test that articles are filtered based on URL content."""
        # Create mock articles
        mock_articles = [
            MagicMock(
                title="News Article",
                html=MagicMock(requested_url="http://example.com/news/story"),
                publishing_date=date.today(),
                authors=["Author 1"],
                body="News content"
            ),
            MagicMock(
                title="Opinion Piece",
                html=MagicMock(requested_url="http://example.com/opinion/story"),
                publishing_date=date.today(),
                authors=["Author 2"],
                body="Opinion content"
            )
        ]
        
        # Configure mock to return our test articles
        mock_article.objects.filter.return_value = mock_articles
        
        # Run crawler
        articles = self.crawler.run_crawler()
        
        # Verify filtering
        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0]["title"], "News Article")

    def test_empty_include_terms(self):
        """Test that empty include terms are handled correctly."""
        with self.assertRaises(ValueError):
            UrlFilterCrawler(
                filter_include_terms=[],
                filter_out_terms=["opinion"],
                timeout_seconds=10
            )


if __name__ == "__main__":
    unittest.main()
