import os
import sys
import shutil
import subprocess
from setuptools import setup
from setuptools.command.build_py import build_py


class CustomBuildPy(build_py):
    def run(self):
        # --- Step 1: Run tests before building — abort if any fail ---
        print("Running tests before build...")
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "test/", "-v"],
            cwd=os.path.abspath("."),
        )
        if result.returncode != 0:
            raise SystemExit("❌ Tests failed — aborting build.")
        print("✅ All tests passed — proceeding with build.\n")

        # --- Step 2: Standard build ---
        super().run()

        # Get the workspace root
        workspace_root = os.environ.get("PWD")
        if not workspace_root or not os.path.exists(os.path.join(workspace_root, "pyproject.toml")):
            workspace_root = os.path.abspath(".")

        dist_dir = os.path.join(workspace_root, "dist")
        os.makedirs(dist_dir, exist_ok=True)

        # --- Step 3: Copy shell scripts to dist/ ---
        scripts = [
            "run_daily_summary.sh",
            "setup_daily_summary_cron.sh",
            "setup_env.sh",
        ]
        for script in scripts:
            src = os.path.join(workspace_root, "src", "software_eng_articles", script)
            dest = os.path.join(dist_dir, script)
            if os.path.exists(src):
                shutil.copy(src, dest)
                os.chmod(dest, 0o755)
                print(f"Post-Build: Copied and chmod+x {script} to {dest}")
            else:
                print(f"Post-Build Warning: {script} not found at {src}")

        # --- Step 4: Copy prompts.toml.template to dist/ ---
        src_tmpl = os.path.join(workspace_root, "prompts.toml.template")
        dest_tmpl = os.path.join(dist_dir, "prompts.toml.template")
        if os.path.exists(src_tmpl):
            shutil.copy(src_tmpl, dest_tmpl)
            print(f"Post-Build: Copied prompts.toml.template to {dest_tmpl}")
        else:
            print(f"Post-Build Warning: prompts.toml.template not found at {src_tmpl}")


setup(
    cmdclass={
        "build_py": CustomBuildPy,
    }
)
