"""Tests for the API endpoints."""

import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from api import app


class TestApi(unittest.TestCase):
    """Test cases for the API endpoints."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = TestClient(app)
        # Default parameters that satisfy CrawlerParams validation
        self.default_params = {
            "max_articles": 5,
            "days_back": 7,
            "timeout": 25
        }

    def test_crawl_body_required_params(self):
        """Test that /crawl/body requires keywords_include."""
        response = self.client.get("/crawl/body", params=self.default_params)
        self.assertEqual(response.status_code, 422)  # Validation error

    def test_crawl_body_with_keywords(self):
        """Test /crawl/body with valid keywords."""
        with patch("api.BodyFilterCrawler") as mock_crawler:
            # Mock the crawler's behavior
            mock_instance = MagicMock()
            mock_instance.run_crawler.return_value = [{
                "title": "Test Article",
                "html": MagicMock(requested_url="http://example.com/test"),
                "publishing_date": "2024-03-14",
                "body": "Test content",
                "authors": ["Test Author"]
            }]
            mock_crawler.return_value = mock_instance

            # Send keywords as query parameters
            params = {
                **self.default_params,
                "keywords_include": ["test", "python"]
            }
            response = self.client.get("/crawl/body", params=params)
            
            if response.status_code != 200:
                print(f"Error response: {response.json()}")  # Print error details
            
            self.assertEqual(response.status_code, 200)
            response_data = response.json()
            self.assertIn("articles", response_data)
            self.assertEqual(len(response_data["articles"]), 1)
            self.assertEqual(response_data["articles"][0]["title"], "Test Article")

    def test_crawl_url_required_params(self):
        """Test that /crawl/url requires keywords_include."""
        response = self.client.get("/crawl/url", params=self.default_params)
        self.assertEqual(response.status_code, 422)  # Validation error

    def test_crawl_url_with_keywords(self):
        """Test /crawl/url with valid keywords."""
        with patch("api.UrlFilterCrawler") as mock_crawler:
            # Mock the crawler's behavior
            mock_instance = MagicMock()
            mock_instance.run_crawler.return_value = [{
                "title": "Test Article",
                "html": MagicMock(requested_url="http://example.com/test"),
                "publishing_date": "2024-03-14",
                "body": "Test content",
                "authors": ["Test Author"]
            }]
            mock_crawler.return_value = mock_instance

            params = {
                **self.default_params,
                "keywords_include": ["test"],
                "keywords_exclude": ["opinion"]
            }
            response = self.client.get("/crawl/url", params=params)

            self.assertEqual(response.status_code, 200)
            response_data = response.json()
            self.assertIn("articles", response_data)
            self.assertEqual(len(response_data["articles"]), 1)

    def test_invalid_source(self):
        """Test handling of invalid news source."""
        params = {
            **self.default_params,
            "keywords_include": ["test"],
            "sources": "InvalidSource"
        }
        response = self.client.get("/crawl/body", params=params)
        self.assertEqual(response.status_code, 400)  # Bad request

    def test_timeout_parameter(self):
        """Test that timeout parameter is respected."""
        with patch("api.BodyFilterCrawler") as mock_crawler:
            mock_instance = MagicMock()
            mock_instance.run_crawler.return_value = [{
                "title": "Test Article",
                "html": MagicMock(requested_url="http://example.com/test"),
                "publishing_date": "2024-03-14",
                "body": "Test content",
                "authors": ["Test Author"]
            }]
            mock_crawler.return_value = mock_instance

            params = {
                **self.default_params,
                "keywords_include": ["test"],
                "timeout": "30"
            }
            response = self.client.get("/crawl/body", params=params)
            
            self.assertEqual(response.status_code, 200)
            # Check that the crawler was called with the correct timeout
            mock_crawler.assert_called_once()
            call_args = mock_crawler.call_args[1]
            self.assertEqual(call_args["timeout_seconds"], 30)

    def test_multiple_keywords_comma_separated(self):
        """Test handling of comma-separated keywords."""
        with patch("api.BodyFilterCrawler") as mock_crawler:
            mock_instance = MagicMock()
            mock_instance.run_crawler.return_value = [{
                "title": "Test Article",
                "html": MagicMock(requested_url="http://example.com/test"),
                "publishing_date": "2024-03-14",
                "body": "Test content",
                "authors": ["Test Author"]
            }]
            mock_crawler.return_value = mock_instance

            params = {
                **self.default_params,
                "keywords_include": "test,python,coding"
            }
            response = self.client.get("/crawl/body", params=params)
            self.assertEqual(response.status_code, 200)

    def test_multiple_keywords_repeated_params(self):
        """Test handling of multiple keyword parameters."""
        with patch("api.BodyFilterCrawler") as mock_crawler:
            mock_instance = MagicMock()
            mock_instance.run_crawler.return_value = [{
                "title": "Test Article",
                "html": MagicMock(requested_url="http://example.com/test"),
                "publishing_date": "2024-03-14",
                "body": "Test content",
                "authors": ["Test Author"]
            }]
            mock_crawler.return_value = mock_instance

            params = {
                **self.default_params,
                "keywords_include": ["test", "python", "coding"]
            }
            response = self.client.get("/crawl/body", params=params)
            self.assertEqual(response.status_code, 200)

    def test_url_filtering_exclude_terms(self):
        """Test URL filtering with exclude terms."""
        with patch("api.UrlFilterCrawler") as mock_crawler:
            mock_instance = MagicMock()
            mock_instance.run_crawler.return_value = [{
                "title": "Test Article",
                "html": MagicMock(requested_url="http://example.com/test"),
                "publishing_date": "2024-03-14",
                "body": "Test content",
                "authors": ["Test Author"]
            }]
            mock_crawler.return_value = mock_instance

            params = {
                **self.default_params,
                "keywords_include": ["news"],
                "keywords_exclude": ["opinion", "podcast"]
            }
            response = self.client.get("/crawl/url", params=params)
            
            self.assertEqual(response.status_code, 200)
            # Verify that both exclude terms were passed to the crawler
            mock_crawler.assert_called_once()
            call_args = mock_crawler.call_args[1]
            self.assertEqual(call_args["filter_include_terms"], ["news"])
            self.assertEqual(call_args["filter_out_terms"], ["opinion", "podcast"])


if __name__ == "__main__":
    unittest.main()
