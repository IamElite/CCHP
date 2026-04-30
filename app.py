import os
import subprocess
import sys

# =============================================================================
# AUTO-UPDATER: Fetch latest code from upstream on every restart
# =============================================================================
print("Checking for updates from upstream repository...")
try:
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--upgrade", "git+https://github.com/Alishahryar1/free-claude-code.git"],
        check=True,
        capture_output=True
    )
    print("Update successful or already up to date.")
except Exception as e:
    print(f"Update failed (using cached version): {e}")

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
