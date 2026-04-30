# Free Claude Code Proxy - Heroku Deploy

This is a minimal deployment package for the Free Claude Code Proxy.

## 1-Click Deployment

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/IamElite/CCHP)

> [!NOTE]
> Make sure to set your **NVIDIA_NIM_API_KEY** in the configuration screen during deployment.

## Features
- **Dyno Size**: `standard-2x` for high performance.
- **Auto-Sync**: Pulls the latest code from the upstream repository.
- **Flexible**: Change models via Heroku Config Vars.

## How to use locally
```powershell
$env:ANTHROPIC_AUTH_TOKEN="heroku"; $env:ANTHROPIC_BASE_URL="https://your-app-name.herokuapp.com"; claude
```
