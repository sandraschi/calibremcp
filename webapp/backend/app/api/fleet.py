"""Dynamic fleet discovery — probe known fleet ports, return which apps are up.

Replaces the hardcoded APPS_CATALOG and CONTAINER_LINKS in the frontend.
"""

import asyncio
import logging

import httpx
from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter()

# ── Fleet webapp catalog (port → label, description) ─────────────────────────
# Source of truth: D:\Dev\repos\mcp-central-docs\operations\WEBAPP_PORTS.md
FLEET_APPS: list[dict] = [
    {"port": 10700, "label": "Virtualization MCP", "desc": "Manage VMs: create, start, stop, snapshot."},
    {"port": 10704, "label": "Advanced Memory", "desc": "Knowledge base: notes, research, graph-based second brain."},
    {"port": 10706, "label": "Robotics MCP", "desc": "Robot control and automation (Unitree, etc.)."},
    {"port": 10708, "label": "Database Ops MCP", "desc": "Database queries, migrations, backups."},
    {"port": 10721, "label": "Calibre MCP", "desc": "This app. E-book library management and search."},
    {"port": 10724, "label": "MCP Studio", "desc": "MCP server management and monitoring studio."},
    {"port": 10726, "label": "Depot MCP", "desc": "Artifact depot and cross-repo lookups."},
    {"port": 10728, "label": "Ring MCP", "desc": "Ring doorbells and cameras."},
    {"port": 10741, "label": "Plex MCP", "desc": "Plex media server: browse and control playback."},
    {"port": 10746, "label": "AutoHotkey MCP", "desc": "AHK automation and scriptlet bridge."},
    {"port": 10748, "label": "Windows Ops MCP", "desc": "Windows system operations and automation."},
    {"port": 10756, "label": "Discord MCP", "desc": "Discord chat and server management."},
    {"port": 10762, "label": "WinRAR MCP", "desc": "Archive management via WinRAR."},
    {"port": 10770, "label": "arXiv MCP", "desc": "arXiv research papers: search, metadata, full text."},
    {"port": 10780, "label": "Browser MCP", "desc": "Browser control and bookmarks dashboard."},
    {"port": 10782, "label": "Home Assistant MCP", "desc": "Smart home: devices, automations, dashboards."},
    {"port": 10788, "label": "Windows CUA MCP", "desc": "Computer Use Agent for Windows automation."},
    {"port": 10792, "label": "Avatar MCP", "desc": "Talking avatars and voice AI."},
    {"port": 10802, "label": "Bookmarks MCP", "desc": "Cross-browser bookmarks management."},
    {"port": 10806, "label": "Docker MCP", "desc": "Docker container management."},
    {"port": 10810, "label": "Notion MCP", "desc": "Notion workspace integration."},
    {"port": 10812, "label": "Email MCP", "desc": "Email client: read, send, search, organize."},
    {"port": 10818, "label": "OBS MCP", "desc": "OBS Studio: streaming and recording control."},
    {"port": 10820, "label": "Tailscale MCP", "desc": "Tailscale mesh VPN management."},
    {"port": 10832, "label": "Local LLM MCP", "desc": "Local LLM inference management (Ollama, etc.)."},
    {"port": 10840, "label": "Beyond Compare MCP", "desc": "File comparison and merge."},
    {"port": 10844, "label": "FastSearch MCP", "desc": "Fast file content search across drives."},
    {"port": 10848, "label": "Blender MCP", "desc": "3D creation suite: modeling, animation, rendering."},
    {"port": 10858, "label": "OCR MCP", "desc": "Optical character recognition and text extraction."},
    {"port": 10860, "label": "System Admin MCP", "desc": "System administration tools."},
    {"port": 10890, "label": "Obsidian MCP", "desc": "Obsidian vault integration."},
    {"port": 10892, "label": "Yahboom MCP", "desc": "Yahboom robotics control."},
    {"port": 10910, "label": "rTorrent MCP", "desc": "Torrent client management."},
    {"port": 10934, "label": "Jellyfin MCP", "desc": "Jellyfin media server: browse and control."},
    {"port": 10944, "label": "FreeCAD MCP", "desc": "Parametric 3D CAD modelling."},
    {"port": 10950, "label": "Opencode CLI MCP", "desc": "Opencode CLI tool integration."},
    {"port": 10966, "label": "QCAD MCP", "desc": "2D CAD technical drawing."},
    {"port": 10978, "label": "Resonite MCP", "desc": "Social VR platform: worlds, assets, networking."},
    {"port": 10981, "label": "LibreOffice MCP", "desc": "Office suite: convert, template gallery."},
    {"port": 10986, "label": "Games App", "desc": "Game library, launches, and metadata."},
    {"port": 10992, "label": "Godot MCP", "desc": "Godot game engine: scenes, scripts, builds."},
    {"port": 10998, "label": "Scraper MCP", "desc": "Web scraping and data extraction."},
    {"port": 11010, "label": "GrandOrgue MCP", "desc": "Virtual pipe organ MIDI control."},
    {"port": 11014, "label": "Google AI MCP", "desc": "Google AI services: Gemini, Veo, Imagen, TTS."},
    {"port": 11016, "label": "KiCad MCP", "desc": "PCB design and electronics CAD."},
    {"port": 11020, "label": "Steam MCP", "desc": "Steam library and friends integration."},
    {"port": 11022, "label": "Chip Design MCP", "desc": "VLSI and EDA orchestration."},
    {"port": 11028, "label": "Inkscape MCP", "desc": "Vector graphics and SVG editing."},
    {"port": 11044, "label": "LimX Robotics MCP", "desc": "LimX robot simulation and control."},
    {"port": 11050, "label": "ROS MCP", "desc": "Robot Operating System bridge."},
    {"port": 10901, "label": "Teleoperator MCP", "desc": "WebXR teleoperation client."},
    {"port": 10976, "label": "UITARS MCP", "desc": "GUI automation agents."},
]

# ── Container ports to probe (Docker / monitoring / infrastructure) ──────────
CONTAINER_PORTS: list[dict] = [
    {"port": 9001, "label": "Portainer", "desc": "Docker container management UI."},
    {"port": 8080, "label": "Traefik", "desc": "Reverse proxy and load balancer."},
    {"port": 3100, "label": "Grafana", "desc": "Observability dashboards."},
    {"port": 9090, "label": "Prometheus", "desc": "Metrics collection and alerting."},
    {"port": 12000, "label": "Fleet Grafana", "desc": "Unified fleet Grafana (mcp-central-docs)."},
    {"port": 12001, "label": "Fleet Prometheus", "desc": "Unified fleet Prometheus."},
    {"port": 3060, "label": "MyAI Dashboard", "desc": "Central microservices dashboard."},
    {"port": 10734, "label": "MyAI Calibre Plus", "desc": "MyAI Calibre library UI."},
    {"port": 10760, "label": "MyAI Plex Plus", "desc": "MyAI Plex frontend."},
    {"port": 10903, "label": "Document Viewer", "desc": "MyAI document viewer container."},
    {"port": 10904, "label": "Future You", "desc": "MyAI future-self AI container."},
    {"port": 10905, "label": "Stable Diffusion", "desc": "MyAI image generation container."},
]

PROBE_TIMEOUT = 1.5
PROBE_MAX_CONCURRENT = 30


async def _probe_port(client: httpx.AsyncClient, port: int) -> bool:
    """Check if a TCP port is listening on localhost (shared client)."""
    try:
        r = await client.get(f"http://127.0.0.1:{port}/")
        return r.status_code < 500
    except Exception:
        return False


@router.get("/fleet/webapps")
async def fleet_webapps() -> dict:
    """Return fleet webapp status: which apps are up, with metadata.

    Probes all known fleet ports in parallel. Also returns container port status.
    Replaces the hardcoded APPS_CATALOG / CONTAINER_LINKS in the frontend.
    """
    # Build unique probe list (dedupe ports)
    webapp_ports = {a["port"] for a in FLEET_APPS}
    container_ports = {c["port"] for c in CONTAINER_PORTS} - webapp_ports
    all_ports = sorted(webapp_ports | container_ports)

    sem = asyncio.Semaphore(PROBE_MAX_CONCURRENT)
    async with httpx.AsyncClient(timeout=PROBE_TIMEOUT) as client:

        async def _probe_with_sem(port: int) -> tuple[int, bool]:
            async with sem:
                return port, await _probe_port(client, port)

        probe_results = await asyncio.gather(*(_probe_with_sem(p) for p in all_ports), return_exceptions=True)

    results: dict[int, bool] = {}
    for item in probe_results:
        if isinstance(item, tuple):
            results[item[0]] = item[1]
        else:
            logger.warning("Probe exception: %s", item)

    up_count = sum(1 for v in results.values() if v)

    # Build webapp list
    webapps = []
    for app in FLEET_APPS:
        port = app["port"]
        webapps.append(
            {
                "label": app["label"],
                "port": port,
                "url": f"http://127.0.0.1:{port}/",
                "description": app["desc"],
                "up": results.get(port, False),
            }
        )

    # Build container list
    containers = []
    for c in CONTAINER_PORTS:
        port = c["port"]
        containers.append(
            {
                "label": c["label"],
                "port": port,
                "url": f"http://127.0.0.1:{port}/",
                "description": c["desc"],
                "up": results.get(port, False),
            }
        )

    return {
        "webapps": webapps,
        "containers": containers,
        "total": len(webapps),
        "total_up": up_count,
    }
