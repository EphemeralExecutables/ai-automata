# Plan: Automated Daily Software Engineering Articles Summary (via agy CLI)

This plan outlines the design and implementation of an automated daily pipeline that fetches software engineering summaries using the Gemini model via the local `agy` CLI, and writes the output to a local directory.

---

## Current vs Proposed Project Structure

### Current Structure
```text
/Users/mattswart/Source/Python/ai-automata/
├── .vscode/
│   └── tasks.json
├── docs/
│   ├── software-engineering-articles-plan.md
│   └── oauth-setup-guide.md
├── src/
│   └── software_eng_articles/
│       ├── daily_software_eng_articles.py
│       └── run_daily_summary.sh
├── test/
│   └── test_summary.py
├── README.md
└── .gitignore
```

### Proposed Structure
```text
/Users/mattswart/Source/Python/ai-automata/
├── .vscode/
│   └── tasks.json                       # VS Code default build task configuration (Shift-Cmd-B)
├── docs/
│   ├── software-engineering-articles-plan.md
│   └── session-summary.md               # Session progress handoff summary
├── src/
│   └── software_eng_articles/           # Dedicated package directory
│       ├── daily_software_eng_articles.py # Python pipeline module
│       ├── run_daily_summary.sh         # Shell wrapper execution entrypoint
│       └── setup_daily_summary_cron.sh  # Cron installation/uninstallation utility script
├── test/
│   └── test_summary.py                  # Automated validation running imports from build/
├── build/                               # Directory for compiled/built python packages (Ignored by git)
├── dist/                                # Directory containing built distribution wheels, wrapper script, and .env configuration
├── .env                                 # Local environment variables (Ignored by git)
├── .env.template                        # Template for local environment configuration
├── .gitignore                           # Configured to ignore .venv, .env, build/, and dist/
└── README.md
```

---

## Proposed Changes

### Packaging
We will add `setup_daily_summary_cron.sh` to our packaging steps:
*   Update `setup.py` to copy `setup_daily_summary_cron.sh` from the source package to `dist/setup_daily_summary_cron.sh` and make it executable (`chmod +x`).

---

## Verification Plan

### Automated/Local Tests
We will verify each module programmatically:
1. Re-build the package.
2. Run `pytest` inside the virtual environment.

### Manual Verification
> [!IMPORTANT]
> Manual testing of the cron setup script will temporarily install the job into your system's crontab for validation, but the verification plan guarantees it is immediately uninstalled/removed afterward to return your system to a clean state.

1. Execute `dist/setup_daily_summary_cron.sh` to register the cron task.
2. Run `crontab -l` to verify that the cron entry exists.
3. Run `dist/setup_daily_summary_cron.sh --uninstall` to remove the cron task.
4. Run `crontab -l` to verify that the cron entry was removed and the user's crontab is clean.

---

## Implementation Runsheet

### Phase 1: Environment, Isolation & Configuration (Completed)
*   Create a virtual environment.
*   Update `.gitignore`.
*   Configure `requirements.txt`.
*   Create `.env.template` and `.env` containing prompt details.

### Phase 2: Build Pipeline & Test Setup (Completed)
*   Create build configuration in `pyproject.toml`.
*   Add `build/` and `dist/` to `.gitignore`.
*   Write `test_summary.py` test cases.

### Phase 3: Persistence, Wrapper & Sync Output (Completed)
*   Configure file exporting to the configured output path.
*   Create the shell wrapper script.
*   Install the package locally in editable mode.
*   Test wrapper execution.

### Phase 4: Refactor & Relocate Files (Completed)
*   Create package directory `src/software_eng_articles/`.
*   Move `run_daily_summary.sh` to the new folder.
*   Move and rename script to `src/software_eng_articles/daily_software_eng_articles.py`.
*   Update `pyproject.toml` package mapping.
*   Update imports inside `test_summary.py`.
*   Clean build, extract wheel and verify package contents.

### Phase 5: Auto-Install Wheel in Wrapper (Completed)
*   Update wrapper to auto-install wheel when missing from the venv.

### Phase 6: Copy Config and VS Code Integration Setup (Completed)
*   Update `setup.py` to copy `.env` to `dist/`.
*   Create `.vscode/tasks.json` default build task mapping.

### Phase 7: Integrate agy CLI for Direct Prompt Execution (Completed)
*   Remove all Google Cloud console, OAuth client, Google Drive, and RSS Feed parsing dependencies/credentials (removing `feedparser`).
*   Update `.env` and `.env.template` to replace `RSS_FEEDS` with the `PROMPT` configuration.
*   Rework `daily_software_eng_articles.py` to load `PROMPT` from environment and execute `agy --print "$PROMPT"` directly via subprocess.
*   Update `test/test_summary.py` to assert correct subprocess prompt passing and stdout saving.

### Phase 8: Dynamic Timestamped Output File (Completed)
*   Modify `daily_software_eng_articles.py` to format output filenames dynamically using the current system date and time (`YYYYMMDD_HHMM` format), transforming `morning_summary.md` to `morning_summary_20260701_2145.md`.
*   Update tests in `test/test_summary.py` to confirm the timestamp formatting works.
*   Clean build, extract, and execute wrapper script to verify timestamped file generation inside `dist/`.

### Phase 9: Cron Orchestration Setup Script
*   Write `src/software_eng_articles/setup_daily_summary_cron.sh` to:
    1. Resolve its active execution directory (which will be `dist/` when deployed).
    2. Support installing a default daily execution schedule (running daily at 8:00 AM, `0 8 * * *`) when run without arguments.
    3. Support uninstalling the cron job (removing the entry from `crontab`) when invoked with the `--uninstall` flag.
*   Update [`setup.py`](file:///Users/mattswart/Source/Python/ai-automata/setup.py) to automatically copy and `chmod +x` the script to `dist/setup_daily_summary_cron.sh`.
