import os
import subprocess
import sys
import asyncio
import time
import urllib.request
import json
from threading import Thread

# =============================================================================
# GHOST UPDATER: Auto-sync with upstream every X hours without manual restart
# =============================================================================
def run_upgrade():
    print("Ghost Updater: Checking for updates from upstream...")
    try:
        # Get latest commit hash from GitHub API (no 'git' command needed)
        api_url = "https://api.github.com/repos/Alishahryar1/free-claude-code/commits/main"
        headers = {"User-Agent": "Heroku-Ghost-Updater"}
        req = urllib.request.Request(api_url, headers=headers)
        
        with urllib.request.urlopen(req) as response:
            data = json.load(response)
            remote_hash = data["sha"]
        
        # Save hash to a temp file to compare later
        hash_file = "/tmp/last_git_hash"
        last_hash = ""
        if os.path.exists(hash_file):
            with open(hash_file, "r") as f:
                last_hash = f.read().strip()
        
        if remote_hash != last_hash:
            print(f"Ghost Updater: New version detected ({remote_hash}). Updating...")
            # Use -U to ensure it actually updates
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-U", "git+https://github.com/Alishahryar1/free-claude-code.git"],
                check=True,
                capture_output=True
            )
            with open(hash_file, "w") as f:
                f.write(remote_hash)
            
            print("Ghost Updater: Update applied. It will take effect on the next restart (natural or manual).")
        else:
            print("Ghost Updater: Already up to date.")
    except Exception as e:
        print(f"Ghost Updater: Check failed: {e}")

def background_scheduler():
    # Initial check on startup
    run_upgrade()
    while True:
        # Wait 2 hours (as requested)
        time.sleep(2 * 3600)
        run_upgrade()

# Start updater in a separate thread
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
