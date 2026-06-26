import os
import subprocess
import sys
import asyncio
import time
import urllib.request
import json
import tempfile
from threading import Thread

# Conditional import for fcntl (Unix only)
try:
    import fcntl
except ImportError:
    fcntl = None

# =============================================================================
# GHOST UPDATER: Auto-sync with upstream every X hours without manual restart
# =============================================================================
def run_upgrade():
    # Use a lock file to ensure only one worker process runs the update
    temp_dir = tempfile.gettempdir()
    lock_file = os.path.join(temp_dir, "ghost_updater.lock")
    
    lock_fd = None
    try:
        lock_fd = open(lock_file, "w")
        if fcntl:
            try:
                # Acquire an exclusive lock (non-blocking)
                fcntl.lockf(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except (BlockingIOError, IOError):
                # Already being handled by another worker
                return
        else:
            # On Windows/other systems without fcntl, we skip the lock
            # Heroku is Linux, so this is mainly for local development compatibility
            pass
    except Exception as e:
        print(f"Ghost Updater: Lock setup failed: {e}")
        return
    
    print("Ghost Updater: Checking for updates from upstream...")
    try:
        # Get latest commit hash from GitHub API (faster check)
        api_url = "https://api.github.com/repos/Alishahryar1/free-claude-code/commits/main"
        headers = {"User-Agent": "Heroku-Ghost-Updater"}
        req = urllib.request.Request(api_url, headers=headers)
        
        with urllib.request.urlopen(req) as response:
            data = json.load(response)
            remote_hash = data["sha"]
        
        hash_file = os.path.join(temp_dir, "last_git_hash")
        last_hash = ""
        if os.path.exists(hash_file):
            try:
                with open(hash_file, "r") as f:
                    last_hash = f.read().strip()
            except Exception:
                pass
        
        if remote_hash != last_hash:
            print(f"Ghost Updater: New version detected ({remote_hash}). Updating...")
            # Use ZIP archive URL (No 'git' command required!)
            zip_url = "https://github.com/Alishahryar1/free-claude-code/archive/refs/heads/main.zip"
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-U", zip_url],
                capture_output=False,
                text=True
            )
            
            if result.returncode == 0:
                with open(hash_file, "w") as f:
                    f.write(remote_hash)
                print("Ghost Updater: Update applied successfully. It will take effect on the next restart.")
            else:
                print(f"Ghost Updater: Update failed with exit code {result.returncode}. Check logs above.")
        else:
            print("Ghost Updater: Already up to date.")
    except Exception as e:
        print(f"Ghost Updater: Check failed: {e}")
    finally:
        if lock_fd:
            if fcntl:
                try:
                    fcntl.lockf(lock_fd, fcntl.LOCK_UN)
                except Exception:
                    pass
            lock_fd.close()

def background_scheduler():
    # Initial check on startup (wait a few seconds to let workers settle)
    time.sleep(5)
    run_upgrade()
    while True:
        # Wait 2 hours
        time.sleep(2 * 3600)
        run_upgrade()

# Start updater in a separate thread
Thread(target=background_scheduler, daemon=True).start()

import asyncio

import api.services
from api.app import create_asgi_app

# =============================================================================
# HEROKU H15 FIX: Inject heartbeats into SSE streams to prevent idle timeouts
# =============================================================================
def patch_streaming_responses():
    """Monkeypatch api.services to inject heartbeats into all SSE streams."""
    original_sse_response = api.services.anthropic_sse_streaming_response

    async def heartbeat_wrapper(body, interval=20):
        """Wrap an async iterator and yield heartbeats if it stays idle.
        
        Uses a non-cancelling approach to preserve upstream stream integrity.
        """
        # 1. Send an initial heartbeat immediately to flush headers and reset Heroku timer
        yield ": heartbeat\n\n"
        
        it = body.__aiter__()
        # We use a task to pull data so we can wait on it without cancelling it
        next_task = asyncio.create_task(it.__anext__())
        
        try:
            while True:
                # Wait for either data or timeout
                done, pending = await asyncio.wait(
                    [next_task], 
                    timeout=interval, 
                    return_when=asyncio.FIRST_COMPLETED
                )
                
                if next_task in done:
                    try:
                        result = next_task.result()
                        yield result
                        # Prepare the next data fetch task
                        next_task = asyncio.create_task(it.__anext__())
                    except StopAsyncIteration:
                        break
                else:
                    # Timeout: Send heartbeat and keep waiting for the same task
                    yield ": heartbeat\n\n"
        except Exception:
            # Clean up the pending task if something goes wrong
            if not next_task.done():
                next_task.cancel()
            raise
        finally:
            # Ensure task is not left dangling
            if not next_task.done():
                next_task.cancel()

    def patched_sse_response(body):
        return original_sse_response(heartbeat_wrapper(body))

    api.services.anthropic_sse_streaming_response = patched_sse_response
    print("Heroku H15 Fix: Heartbeat patch applied to streaming responses.")

# Apply the patch before creating the app
patch_streaming_responses()

app = create_asgi_app()
