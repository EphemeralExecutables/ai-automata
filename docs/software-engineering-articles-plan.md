# Plan: Automated Daily Software Engineering Articles Summary

This plan outlines the design and implementation of an automated daily pipeline that fetches software engineering articles from various tech RSS feeds, summarizes them using Gemini (via the `google-genai` SDK and OAuth 2.0), and writes the output to a local directory and uploads it directly to Google Drive.

## Goal Description
The objective is to run a daily, headless cron job on a Linux machine that:
1. Parses predefined technology and software engineering RSS feeds.
2. Authenticates headlessly with Gemini using a cached OAuth 2.0 `token.json` generated from a Google Cloud Desktop App credentials file (`client_secret.json`).
3. Sends the compiled feed content to the Gemini API (`gemini-2.5-flash`) for a structured morning summary.
4. Appends/writes the markdown-formatted summary to a local synced file.
5. Uploads the generated summary directly to a specified Google Drive folder via the Google Drive API.

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
│   ├── oauth-setup-guide.md             # OAuth setup instructions
│   └── google-drive-setup-guide.md      # Google Drive API configuration instructions
├── src/
│   └── software_eng_articles/           # Dedicated package directory
│       ├── daily_software_eng_articles.py # Renamed python pipeline module
│       └── run_daily_summary.sh         # Relocated shell wrapper entrypoint script
├── test/
│   └── test_summary.py                  # Automated validation running imports from the build/ directory
├── build/                               # Directory for compiled/built python packages (Ignored by git)
├── dist/                                # Directory containing built distribution wheels, wrapper script, and .env configuration
├── .env                                 # Local environment variables (Ignored by git)
├── .env.template                        # Template for local environment configuration
├── .gitignore                           # Configured to ignore .venv, .env, token.json, build/, and client_secret.json
└── README.md
```

---

## Proposed Changes

### Dependencies
We need to add the Google API Client library to interact with Google Drive:
*   `google-api-python-client`

### Configuration
We will add configuration options to `.env` to support Google Drive target folder:
*   `GD_FOLDER_ID`: The specific Google Drive folder ID where the morning summaries should be uploaded.

---

## Verification Plan

### Automated/Local Tests
We will verify each module programmatically:
1. Re-build the package with the new package path structure.
2. Update tests in `test/test_summary.py` to import from the new module layout in `build/`.
3. Run `pytest` inside the virtual environment.

### Manual Verification
1. Open the project inside VS Code and verify that pressing `Shift-Cmd-B` initiates a clean build.
2. Execute the summary wrapper script and confirm that the file is successfully created locally in `dist/` and uploaded to the Google Drive folder.

---

## Implementation Runsheet

### Phase 1: Environment, Isolation & Configuration (Completed)
*   Create a virtual environment: `python3 -m venv .venv`.
*   Update [`.gitignore`](file:///Users/mattswart/Source/Python/ai-automata/.gitignore) to exclude `.env`, `.venv/`, and `token.json`.
*   Create [`requirements.txt`](file:///Users/mattswart/Source/Python/ai-automata/requirements.txt) with all required library versions.
*   Activate the virtual environment (`source .venv/bin/activate`) and install dependencies: `pip install -r requirements.txt`.
*   Create [`.env.template`](file:///Users/mattswart/Source/Python/ai-automata/.env.template) defining feed lists, file paths, and model configurations.
*   Create a local `.env` file containing actual values for local testing.

### Phase 2: Build Pipeline & Test Setup (Completed)
*   Create build configuration in `pyproject.toml` to package the `src/` modules.
*   Add `build/` and `dist/` to `.gitignore`.
*   Write [`test_summary.py`](file:///Users/mattswart/Source/Python/ai-automata/test/test_summary.py) test cases to verify pipeline functions.
*   Ensure the test runner runs tests directly against the modules located in `build/`.

### Phase 3: Persistence, Wrapper & Sync Output (Completed)
*   Configure file exporting to the configured output path.
*   Create the shell wrapper script [`run_daily_summary.sh`](file:///Users/mattswart/Source/Python/ai-automata/run_daily_summary.sh) that activates the `.venv` and executes the `daily-summary` command.
*   Install the package locally in editable mode (`pip install -e .`) so changes are immediately testable without rebuilds.
*   Test end-to-end execution of the wrapper.

### Phase 4: Refactor & Relocate Files (Completed)
*   Create package directory `src/software_eng_articles/`.
*   Move `run_daily_summary.sh` to the new folder and update relative path resolver inside it.
*   Move and rename `src/daily_summary.py` to `src/software_eng_articles/daily_software_eng_articles.py`.
*   Update [`pyproject.toml`](file:///Users/mattswart/Source/Python/ai-automata/pyproject.toml) to map the new package, specify package entrypoint, and include `.sh` wrapper script in package data.
*   Update imports inside [`test/test_summary.py`](file:///Users/mattswart/Source/Python/ai-automata/test/test_summary.py).
*   Clean build, extract wheel to `build/` and verify package contents.

### Phase 5: Auto-Install Wheel in Wrapper (Completed)
*   Update [`run_daily_summary.sh`](file:///Users/mattswart/Source/Python/ai-automata/src/software_eng_articles/run_daily_summary.sh) to check the execution folder for a wheel file (`*.whl`) and auto-install it.
*   Test execution logic in `dist/`.

### Phase 6: Copy Config and VS Code Integration Setup (Completed)
*   Update [`setup.py`](file:///Users/mattswart/Source/Python/ai-automata/setup.py) to copy `.env` to `dist/`.
*   Create [`.vscode/tasks.json`](file:///Users/mattswart/Source/Python/ai-automata/.vscode/tasks.json) defining the default build task.
*   Perform clean build and verify copying actions.

### Phase 7: Credentials & Handshake Setup
*   Implement OAuth initialization and silent token refreshes inside `daily_software_eng_articles.py`.
*   Guide user to follow [oauth-setup-guide.md](file:///Users/mattswart/Source/Python/ai-automata/docs/oauth-setup-guide.md) to download `client_secret.json` and generate `token.json`.

### Phase 8: Google Drive Integration
*   Enable Google Drive API in Google Cloud Console.
*   Expand OAuth scopes in `daily_software_eng_articles.py` to include `https://www.googleapis.com/auth/drive.file`.
*   Add `google-api-python-client` to `requirements.txt` and `pyproject.toml`.
*   Write Google Drive file creation/upload helper inside `daily_software_eng_articles.py` using `googleapiclient.discovery`.
*   Write [google-drive-setup-guide.md](file:///Users/mattswart/Source/Python/ai-automata/docs/google-drive-setup-guide.md) documentation.

### Phase 9: Feed Processing & API Integration
*   Write RSS parsing logic to extract articles.
*   Format feed outputs into a concise context payload.
*   Integrate SDK call to request the summary from the configured model (e.g. `gemini-2.5-flash`).

### Phase 10: Cron Orchestration
*   Define the exact daily cron schedule command for execution on the target Linux system, pointing to the relocated shell wrapper script.
