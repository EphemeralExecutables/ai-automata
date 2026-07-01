import os
import sys
import unittest
from unittest.mock import patch, mock_open

# Inject the build directory path to ensure we import from the built code
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../build")))

from software_eng_articles import daily_software_eng_articles as daily_summary

class TestDailySummaryBuild(unittest.TestCase):
    def test_import_origin(self):
        # Assert that the module is imported from the build directory
        self.assertIn("build", daily_summary.__file__)

    def test_get_oauth_credentials_missing_secret(self):
        # Verify that FileNotFoundError is raised if no client secret or token exists
        with self.assertRaises(FileNotFoundError):
            daily_summary.get_oauth_credentials("non_existent_secret.json", "non_existent_token.json")

    @patch("os.path.exists")
    @patch("google.oauth2.credentials.Credentials.from_authorized_user_file")
    def test_get_oauth_credentials_from_cache(self, mock_from_file, mock_exists):
        # Mock that token.json exists
        mock_exists.side_effect = lambda path: path == "mock_token.json"
        # Mock the credentials object as valid
        mock_creds = mock_from_file.return_value
        mock_creds.valid = True

        creds = daily_summary.get_oauth_credentials("mock_secret.json", "mock_token.json")
        self.assertEqual(creds, mock_creds)
        mock_from_file.assert_called_once_with("mock_token.json", daily_summary.SCOPES)

    def test_fetch_articles(self):
        articles = daily_summary.fetch_articles(["https://example.com/rss"])
        self.assertIsInstance(articles, list)
        self.assertGreater(len(articles), 0)
        self.assertEqual(articles[0]["title"], "Mock Article 1")

    @patch("google.genai.Client")
    def test_generate_summary(self, mock_client):
        articles = [{"title": "Test Title", "link": "https://test.com", "summary": "Test Summary"}]
        summary = daily_summary.generate_summary("test_creds", articles, model="test-model")
        self.assertIn("1 articles", summary)
        self.assertIn("test-model", summary)
        mock_client.assert_called_once_with(credentials="test_creds")

if __name__ == "__main__":
    unittest.main()
