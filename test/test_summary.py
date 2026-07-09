import sys
import unittest
import subprocess
import tempfile
import textwrap
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

# Import from source tree
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from software_eng_articles import daily_software_eng_articles as daily_summary


class TestImport(unittest.TestCase):
    def test_import_from_src(self):
        """Module should be loaded from the src tree, not a stale build dir."""
        self.assertIn("src", daily_summary.__file__)

    def test_version_defined(self):
        """__version__ must be a non-empty string."""
        self.assertIsInstance(daily_summary.__version__, str)
        self.assertTrue(len(daily_summary.__version__) > 0)


class TestLoadConfig(unittest.TestCase):
    def _write_toml(self, content: str, path: Path) -> Path:
        path.write_text(textwrap.dedent(content))
        return path

    def test_load_valid_section(self):
        with tempfile.TemporaryDirectory() as tmp:
            toml_path = Path(tmp) / "prompts.toml"
            self._write_toml(
                """
                [java]
                prompt = "Write a Java summary."
                output_path = "./java_summary.md"
                """,
                toml_path,
            )
            config = daily_summary.load_config(toml_path, "java")
            self.assertEqual(config["prompt"], "Write a Java summary.")
            self.assertEqual(config["output_path"], "./java_summary.md")

    def test_missing_section_raises_key_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            toml_path = Path(tmp) / "prompts.toml"
            self._write_toml(
                """
                [cpp]
                prompt = "C++ prompt."
                output_path = "./cpp.md"
                """,
                toml_path,
            )
            with self.assertRaises(KeyError) as ctx:
                daily_summary.load_config(toml_path, "java")
            self.assertIn("java", str(ctx.exception))
            self.assertIn("cpp", str(ctx.exception))  # available sections listed

    def test_missing_file_raises_file_not_found(self):
        with self.assertRaises(FileNotFoundError) as ctx:
            daily_summary.load_config(Path("/nonexistent/prompts.toml"), "java")
        self.assertIn("prompts.toml", str(ctx.exception))


class TestRunAgyPrint(unittest.TestCase):
    @patch("subprocess.run")
    def test_success_returns_stripped_stdout(self, mock_run):
        mock_proc = MagicMock()
        mock_proc.stdout = "  Generated summary.  \n"
        mock_run.return_value = mock_proc

        result = daily_summary.run_agy_print("Test prompt")

        self.assertEqual(result, "Generated summary.")
        mock_run.assert_called_once_with(
            ["agy", "--print", "Test prompt"],
            capture_output=True,
            text=True,
            check=True,
        )

    @patch("subprocess.run")
    def test_called_process_error_raises_runtime_error(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd="agy", stderr="Model quota exceeded"
        )
        with self.assertRaises(RuntimeError) as ctx:
            daily_summary.run_agy_print("Test prompt")
        self.assertIn("Model quota exceeded", str(ctx.exception))

    @patch("subprocess.run")
    def test_missing_agy_raises_file_not_found(self, mock_run):
        mock_run.side_effect = FileNotFoundError()
        with self.assertRaises(FileNotFoundError) as ctx:
            daily_summary.run_agy_print("Test prompt")
        self.assertIn("Antigravity CLI is installed", str(ctx.exception))


class TestMain(unittest.TestCase):
    def _make_toml(self, tmp_dir: Path, section: str, prompt: str, output_path: str) -> Path:
        toml_path = tmp_dir / "prompts.toml"
        toml_path.write_text(
            f'[{section}]\nprompt = "{prompt}"\noutput_path = "{output_path}"\n'
        )
        return toml_path

    @patch("software_eng_articles.daily_software_eng_articles.run_agy_print")
    @patch("software_eng_articles.daily_software_eng_articles.datetime")
    def test_main_writes_timestamped_file(self, mock_datetime, mock_agy):
        """main() should write output to a timestamped path derived from output_path."""
        mock_now = MagicMock()
        mock_now.strftime.return_value = "20260709_2100"
        mock_datetime.datetime.now.return_value = mock_now
        mock_agy.return_value = "Summary content"

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            toml_path = self._make_toml(
                tmp_path,
                section="java",
                prompt="Java prompt.",
                output_path=str(tmp_path / "java_summary.md"),
            )
            output_file = tmp_path / "java_summary_20260709_2100.md"

            with patch("sys.argv", ["daily-summary", "--section", "java", "--config", str(toml_path)]):
                daily_summary.main()

            self.assertTrue(output_file.exists())
            self.assertIn("Summary content", output_file.read_text())

    @patch("software_eng_articles.daily_software_eng_articles.run_agy_print")
    @patch("software_eng_articles.daily_software_eng_articles.datetime")
    def test_main_missing_section_exits(self, mock_datetime, mock_agy):
        """main() should sys.exit(1) when the requested section doesn't exist."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            toml_path = self._make_toml(
                tmp_path, "cpp", "C++ prompt.", str(tmp_path / "cpp.md")
            )
            with patch("sys.argv", ["daily-summary", "--section", "java", "--config", str(toml_path)]):
                with self.assertRaises(SystemExit) as ctx:
                    daily_summary.main()
            self.assertEqual(ctx.exception.code, 1)

    @patch("software_eng_articles.daily_software_eng_articles.run_agy_print")
    @patch("software_eng_articles.daily_software_eng_articles.datetime")
    def test_main_empty_prompt_exits(self, mock_datetime, mock_agy):
        """main() should sys.exit(1) when prompt is empty."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            toml_path = tmp_path / "prompts.toml"
            toml_path.write_text('[java]\nprompt = ""\noutput_path = "./out.md"\n')

            with patch("sys.argv", ["daily-summary", "--section", "java", "--config", str(toml_path)]):
                with self.assertRaises(SystemExit) as ctx:
                    daily_summary.main()
            self.assertEqual(ctx.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
