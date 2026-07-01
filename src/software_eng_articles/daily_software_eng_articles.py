import os
import sys
import subprocess
import datetime
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

def run_agy_print(prompt):
    """Executes the local agy CLI with --print to query the model."""
    try:
        # Run the command: agy --print "prompt"
        # We capture stdout (which contains the model's text response).
        result = subprocess.run(
            ["agy", "--print", prompt],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        err_msg = e.stderr or e.stdout
        print(f"Error executing agy CLI: {err_msg}", file=sys.stderr)
        raise RuntimeError(f"agy CLI failed: {err_msg}")
    except FileNotFoundError:
        raise FileNotFoundError(
            "The 'agy' command-line tool was not found in your system's PATH. "
            "Please ensure that Antigravity CLI is installed and running."
        )

def main():
    # 1. Retrieve config from environment variables
    prompt = os.getenv("PROMPT", "")
    output_path = os.getenv("OUTPUT_PATH", "./morning_summary.md")
    
    if not prompt:
        print("Error: PROMPT environment variable is empty. Please configure it in your .env file.", file=sys.stderr)
        sys.exit(1)
        
    # Append YYYYMMDD_HHMM timestamp to the output filename (preserving path and extension)
    base_path, ext = os.path.splitext(output_path)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    output_path_ts = f"{base_path}_{timestamp}{ext}"
        
    # 2. Run pipeline
    try:
        print("Executing prompt via agy CLI...")
        summary_text = run_agy_print(prompt)
    except Exception as e:
        print(f"Pipeline Execution Error: {e}", file=sys.stderr)
        sys.exit(1)
        
    # 3. Write summary to output file
    output_abs = os.path.abspath(output_path_ts)
    output_dir = os.path.dirname(output_abs)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        
    with open(output_abs, "w") as f:
        f.write(summary_text + "\n")
        
    print(f"Success! Daily summary written to: {output_abs}")

if __name__ == "__main__":
    main()
