import os
import shutil
from setuptools import setup
from setuptools.command.build_py import build_py

class CustomBuildPy(build_py):
    def run(self):
        # First, run the standard build
        super().run()
        
        # Get the original workspace root from the PWD env variable (POSIX shells set this)
        workspace_root = os.environ.get('PWD')
        if not workspace_root or not os.path.exists(os.path.join(workspace_root, "pyproject.toml")):
            # Fallback to current directory if PWD is not set or invalid
            workspace_root = os.path.abspath(".")
            
        dist_dir = os.path.join(workspace_root, "dist")
        os.makedirs(dist_dir, exist_ok=True)
        
        # 1. Copy the shell script to the dist/ directory
        src_sh = os.path.join(workspace_root, "src", "software_eng_articles", "run_daily_summary.sh")
        dest_sh = os.path.join(dist_dir, "run_daily_summary.sh")
        
        if os.path.exists(src_sh):
            shutil.copy(src_sh, dest_sh)
            os.chmod(dest_sh, 0o755)  # Make it executable in dist/
            print(f"Post-Build: Copied and chmod+x wrapper script to {dest_sh}")
        else:
            print(f"Post-Build Warning: Source shell script not found at {src_sh}")
            
        # 2. Copy the cron setup script to the dist/ directory
        src_cron = os.path.join(workspace_root, "src", "software_eng_articles", "setup_daily_summary_cron.sh")
        dest_cron = os.path.join(dist_dir, "setup_daily_summary_cron.sh")
        
        if os.path.exists(src_cron):
            shutil.copy(src_cron, dest_cron)
            os.chmod(dest_cron, 0o755)  # Make it executable in dist/
            print(f"Post-Build: Copied and chmod+x cron setup script to {dest_cron}")
        else:
            print(f"Post-Build Warning: Source cron setup script not found at {src_cron}")
            
        # 3. Copy the environment setup script to the dist/ directory
        src_setup_env = os.path.join(workspace_root, "src", "software_eng_articles", "setup_env.sh")
        dest_setup_env = os.path.join(dist_dir, "setup_env.sh")
        
        if os.path.exists(src_setup_env):
            shutil.copy(src_setup_env, dest_setup_env)
            os.chmod(dest_setup_env, 0o755)  # Make it executable in dist/
            print(f"Post-Build: Copied and chmod+x environment setup script to {dest_setup_env}")
        else:
            print(f"Post-Build Warning: Source environment setup script not found at {src_setup_env}")
            
        # 4. Copy the .env configuration file to the dist/ directory
        src_env = os.path.join(workspace_root, ".env")
        dest_env = os.path.join(dist_dir, ".env")
        
        if os.path.exists(src_env):
            shutil.copy(src_env, dest_env)
            print(f"Post-Build: Copied configuration (.env) file to {dest_env}")
        else:
            print(f"Post-Build Warning: Source .env configuration file not found at {src_env}")

setup(
    cmdclass={
        'build_py': CustomBuildPy,
    }
)
