import os
import sys
import unittest
import subprocess
from unittest.mock import patch, MagicMock, mock_open

# Inject the build directory path to ensure we import from the built code
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../build")))

from software_eng_articles import daily_software_eng_articles as daily_summary

class TestDailySummaryBuild(unittest.TestCase):
    def test_import_origin(self):
        # Assert that the module is imported from the build directory
        self.assertIn("build", daily_summary.__file__)

    @patch("subprocess.run")
    def test_run_agy_print_success(self, mock_run):
        # Configure subprocess mock to succeed and return response text
        mock_process = MagicMock()
        mock_process.stdout = "This is the generated summary output."
        mock_run.return_value = mock_process

        result = daily_summary.run_agy_print("Test Prompt")
        self.assertEqual(result, "This is the generated summary output.")
        mock_run.assert_called_once_with(
            ["agy", "--print", "Test Prompt"],
            capture_output=True,
            text=True,
            check=True
        )

    @patch("subprocess.run")
    def test_run_agy_print_command_error(self, mock_run):
        # Mock CalledProcessError when command returns non-zero status
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd="agy",
            stderr="Model quota exceeded"
        )
        with self.assertRaises(RuntimeError) as context:
            daily_summary.run_agy_print("Test Prompt")
        self.assertIn("Model quota exceeded", str(context.exception))

    @patch("subprocess.run")
    def test_run_agy_print_missing_tool(self, mock_run):
        # Mock FileNotFoundError when agy is not installed in system path
        mock_run.side_effect = FileNotFoundError()
        with self.assertRaises(FileNotFoundError) as context:
            daily_summary.run_agy_print("Test Prompt")
        self.assertIn("Antigravity CLI is installed", str(context.exception))

    @patch("software_eng_articles.daily_software_eng_articles.datetime")
    @patch("software_eng_articles.daily_software_eng_articles.run_agy_print")
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.makedirs")
    def test_main_timestamped_filename(self, mock_makedirs, mock_file, mock_print, mock_datetime):
        # Configure datetime mock to return a fixed time
        mock_now = MagicMock()
        mock_now.strftime.return_value = "20260701_2145"
        mock_datetime.datetime.now.return_value = mock_now

        mock_print.return_value = "Summary content"

        # Mock environmental variables
        with patch.dict(os.environ, {"PROMPT": "Query", "OUTPUT_PATH": "./dist/morning_summary.md"}):
            # Run the main program
            daily_summary.main()

            # Verify that it attempted to write to the timestamped path
            expected_path = os.path.abspath("./dist/morning_summary_20260701_2145.md")
            mock_file.assert_called_once_with(expected_path, "w")

if __name__ == "__main__":
    unittest.main()
