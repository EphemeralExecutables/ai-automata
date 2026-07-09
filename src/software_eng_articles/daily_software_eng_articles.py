import sys
import subprocess
import datetime
import argparse
from pathlib import Path
from importlib.metadata import version, PackageNotFoundError

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

# tomllib is built-in from Python 3.11+; fall back to tomli for older versions.
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        raise ImportError(
            "Python < 3.11 requires the 'tomli' package. "
            "Install it with: pip install tomli"
        )

try:
    __version__ = version("ai-automata")
except PackageNotFoundError:
    # Running directly from source without being installed
    __version__ = "dev"

# Default config: look for prompts.toml in the current working directory.
# The run_daily_summary.sh script cd's to the repo root before invoking this,
# so cwd is always the repo root. Using __file__.parents[] breaks when the
# package is installed into site-packages.
_DEFAULT_CONFIG = Path.cwd() / "prompts.toml"

console = Console()
err_console = Console(stderr=True)


def print_header(version: str) -> None:
    """Print a styled banner with the version."""
    title = Text()
    title.append("⚡ AI Automata", style="bold cyan")
    title.append(f"  v{version}", style="dim cyan")
    console.print(Panel(title, box=box.ROUNDED, border_style="cyan", expand=False))


def print_run_info(section: str, config_path: Path, prompt: str, output_path: Path) -> None:
    """Print a rich table summarising the run configuration."""
    table = Table(
        box=box.SIMPLE_HEAVY,
        border_style="bright_black",
        show_header=True,
        header_style="bold magenta",
        title="[bold]Run Configuration[/bold]",
        title_style="magenta",
        min_width=72,
    )
    table.add_column("Key", style="bold yellow", no_wrap=True)
    table.add_column("Value", style="white")

    table.add_row("Section", f"[bold green]\\[{section}][/bold green]")
    table.add_row("Config File", str(config_path))
    table.add_row("Output Path", str(output_path))
    table.add_row(
        "Prompt",
        prompt[:300].replace("\n", " ") + ("…" if len(prompt) > 300 else ""),
    )

    console.print()
    console.print(table)
    console.print()


def print_success(output_abs: Path) -> None:
    """Print a styled success panel."""
    msg = Text()
    msg.append("✅  Summary written to:\n", style="bold green")
    msg.append(str(output_abs), style="bright_white underline")
    console.print(Panel(msg, box=box.ROUNDED, border_style="green"))


def print_error(message: str) -> None:
    """Print a styled error panel to stderr."""
    msg = Text()
    msg.append("❌  Error\n", style="bold red")
    msg.append(message, style="bright_white")
    err_console.print(Panel(msg, box=box.ROUNDED, border_style="red"))


def load_config(config_path: Path, section: str) -> dict:
    """Load and return a single named section from the TOML config file."""
    if not config_path.exists():
        raise FileNotFoundError(
            f"Config file not found: {config_path}\n"
            "Copy prompts.toml.template to prompts.toml and configure your sections."
        )
    with open(config_path, "rb") as f:
        data = tomllib.load(f)

    if section not in data:
        available = ", ".join(data.keys()) or "(none)"
        raise KeyError(
            f"Section '[{section}]' not found in {config_path}.\n"
            f"Available sections: {available}"
        )
    return data[section]


def run_agy_print(prompt: str) -> str:
    """Executes the local agy CLI with --print to query the model."""
    try:
        result = subprocess.run(
            ["agy", "--print", prompt],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        err_msg = e.stderr or e.stdout
        raise RuntimeError(f"agy CLI exited with an error:\n{err_msg}")
    except FileNotFoundError:
        raise FileNotFoundError(
            "The 'agy' command was not found in PATH. "
            "Ensure Antigravity CLI is installed."
        )


def main():
    parser = argparse.ArgumentParser(
        description="Run a named prompt section from prompts.toml via the agy CLI."
    )
    parser.add_argument(
        "--section", "-s",
        required=True,
        help="The [section] name in prompts.toml to execute (e.g. cpp, java).",
    )
    parser.add_argument(
        "--config", "-c",
        type=Path,
        default=_DEFAULT_CONFIG,
        help=f"Path to the TOML config file (default: {_DEFAULT_CONFIG}).",
    )
    args = parser.parse_args()

    print_header(__version__)

    # 1. Load config section
    try:
        config = load_config(args.config, args.section)
    except (FileNotFoundError, KeyError) as e:
        print_error(str(e))
        sys.exit(1)

    prompt = config.get("prompt", "").strip()
    output_path = config.get("output_path", f"./summary_{args.section}.md")

    if not prompt:
        print_error(
            f"'prompt' is empty in section '[{args.section}]' of {args.config}."
        )
        sys.exit(1)

    # 2. Build timestamped output path
    base, ext = str(output_path).rsplit(".", 1) if "." in str(output_path) else (str(output_path), "md")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    output_path_ts = Path(f"{base}_{timestamp}.{ext}")

    # 3. Display run configuration
    print_run_info(args.section, args.config.resolve(), prompt, output_path_ts)

    # 4. Run pipeline
    with console.status(
        f"[bold cyan]Executing prompt via agy CLI…[/bold cyan]", spinner="dots"
    ):
        try:
            summary_text = run_agy_print(prompt)
        except Exception as e:
            print_error(str(e))
            sys.exit(1)

    # 5. Write output
    output_abs = output_path_ts.resolve()
    output_abs.parent.mkdir(parents=True, exist_ok=True)
    output_abs.write_text(summary_text + "\n")

    print_success(output_abs)


if __name__ == "__main__":
    main()
