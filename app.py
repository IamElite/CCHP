import os
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
