"""Launch another MCP webapp by port: check if running, if not run start script and wait until up."""

import logging
import os
import subprocess
import sys
import time
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Port -> (repo_dir_name, script_relative_to_repo). Script is .bat or .ps1.
# REPOS_ROOT env (default D:\\Dev\\repos) is the parent of repo_dir_name.
WEBAPP_LAUNCH_MAP: dict[int, tuple[str, str]] = {
    10700: ("virtualization-mcp", "web/start.bat"),
    10704: ("advanced-memory-mcp", "start-webapp.bat"),
    10706: ("robotics-mcp", "web/start.bat"),
    10708: ("database-operations-mcp", "web/start.bat"),
    10710: ("avatar-mcp", "web/start.bat"),
    10712: ("vrchat-mcp", "web/start.bat"),
    10716: ("tapo-camera-mcp", "webapp/start.bat"),
    10718: ("meta_mcp", "start.bat"),
    10720: ("calibre-mcp", "webapp/start.bat"),
    10721: ("calibre-mcp", "webapp/start.bat"),
    10722: ("mywienerlinien", "start.ps1"),
    10724: ("mcp-studio", "start.bat"),
    10726: ("games-app", "START_GAMES.ps1"),
    10728: ("ring-mcp", "webapp/run-webapp.bat"),
    10738: ("dark-app-factory", "web/start.bat"),
    10741: ("plex-mcp", "webapp/start.bat"),
    3060: ("myai", "core/dashboard/start.ps1"),  # optional; may not exist
}

ALLOWED_PORTS = frozenset(WEBAPP_LAUNCH_MAP)
POLL_INTERVAL = 2
POLL_TIMEOUT = 90


def _repos_root() -> Path:
    root = os.environ.get("REPOS_ROOT", "D:\\Dev\\repos")
    return Path(root)


def _check_port_up(port: int, timeout: float = 3.0) -> bool:
    try:
        import urllib.request
        req = urllib.request.Request(f"http://127.0.0.1:{port}/", method="GET")
        urllib.request.urlopen(req, timeout=timeout)
        return True
    except Exception:
        return False


def _run_start_script(repo_dir: str, script_rel: str) -> None:
    root = _repos_root()
    repo_path = root / repo_dir
    script_path = repo_path / script_rel
    if not script_path.exists():
        raise FileNotFoundError(f"Start script not found: {script_path}")
    cmd: list[str]
    if script_path.suffix.lower() == ".ps1":
        cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(script_path)]
        if repo_dir == "mywienerlinien":
            cmd.append("start")
    else:
        cmd = ["cmd.exe", "/c", str(script_path)]
    # Start in new console (Windows) so the script runs in its own window and we don't block
    creationflags = 0
    if sys.platform == "win32":
        creationflags = subprocess.CREATE_NEW_CONSOLE
    subprocess.Popen(
        cmd,
        cwd=str(repo_path),
        creationflags=creationflags,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    logger.info("Started webapp launch process: %s in %s", script_rel, repo_path)


class WebappLaunchRequest(BaseModel):
    port: int


class WebappLaunchResponse(BaseModel):
    already_running: bool
    started: bool
    url: str
    error: str | None = None


router = APIRouter()


@router.post("/webapp-launch", response_model=WebappLaunchResponse)
async def webapp_launch(body: WebappLaunchRequest) -> WebappLaunchResponse:
    port = body.port
    if port not in ALLOWED_PORTS:
        raise HTTPException(status_code=400, detail=f"Port {port} is not allowed for launch")
    url = f"http://127.0.0.1:{port}/"
    if _check_port_up(port):
        return WebappLaunchResponse(already_running=True, started=False, url=url)
    repo_dir, script_rel = WEBAPP_LAUNCH_MAP[port]
    try:
        _run_start_script(repo_dir, script_rel)
    except FileNotFoundError as e:
        logger.warning("Webapp launch script missing: %s", e)
        return WebappLaunchResponse(
            already_running=False, started=False, url=url, error=str(e)
        )
    except Exception as e:
        logger.exception("Webapp launch failed: %s", e)
        return WebappLaunchResponse(
            already_running=False, started=False, url=url, error=str(e)
        )
    # Poll until up or timeout
    deadline = time.monotonic() + POLL_TIMEOUT
    while time.monotonic() < deadline:
        time.sleep(POLL_INTERVAL)
        if _check_port_up(port):
            return WebappLaunchResponse(already_running=False, started=True, url=url)
    return WebappLaunchResponse(
        already_running=False, started=False, url=url, error="Timeout waiting for webapp to start"
    )
