import os
import subprocess
import sys
import asyncio
import time
from threading import Thread

# =============================================================================
# GHOST UPDATER: Auto-sync with upstream every 6 hours without manual restart
# =============================================================================
def run_upgrade():
    print("Ghost Updater: Checking for updates from upstream...")
    try:
        # Check if there's actually a new commit to avoid unnecessary restarts
        # We use git ls-remote to get the latest hash
        remote_hash = subprocess.check_output(
            ["git", "ls-remote", "https://github.com/Alishahryar1/free-claude-code.git", "HEAD"]
        ).split()[0].decode()
        
        # Save hash to a temp file to compare later
        hash_file = "/tmp/last_git_hash"
        last_hash = ""
        if os.path.exists(hash_file):
            with open(hash_file, "r") as f:
                last_hash = f.read().strip()
        
        if remote_hash != last_hash:
            print(f"Ghost Updater: New version detected ({remote_hash}). Updating...")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "--upgrade", "git+https://github.com/Alishahryar1/free-claude-code.git"],
                check=True,
                capture_output=True
            )
            with open(hash_file, "w") as f:
                f.write(remote_hash)
            
            print("Ghost Updater: Update applied. Restarting server to activate...")
            # Magic restart: replaces current process with a new one
            os.execv(sys.executable, [sys.executable] + sys.argv)
        else:
            print("Ghost Updater: Already up to date.")
    except Exception as e:
        print(f"Ghost Updater: Check failed: {e}")

def background_scheduler():
    # Initial check on startup
    run_upgrade()
    while True:
        # Wait 6 hours
        time.sleep(6 * 3600)
        run_upgrade()

# Start updater in a separate thread so it doesn't block FastAPI
Thread(target=background_scheduler, daemon=True).start()

from api.app import create_asgi_app
from config.settings import get_settings

# =============================================================================
# Heroku Configuration (Default Values)
# =============================================================================
os.environ.setdefault("NVIDIA_NIM_API_KEY", "your_api_key_here")
os.environ.setdefault("ANTHROPIC_AUTH_TOKEN", "heroku")

os.environ.setdefault("MODEL", "nvidia_nim/z-ai/glm4.7")
os.environ.setdefault("MODEL_OPUS", "nvidia_nim/deepseek-ai/deepseek-v4-pro")
os.environ.setdefault("MODEL_SONNET", "nvidia_nim/z-ai/glm4.7")
os.environ.setdefault("MODEL_HAIKU", "nvidia_nim/deepseek-ai/deepseek-v4-flash")

# Get settings instance
settings = get_settings()

app = create_asgi_app()
