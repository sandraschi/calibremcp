/**
 * Catalog of webapps in "Our Apps". Single source of truth for the dropdown and the apps page.
 * Written for normal users: what the app is, and what the MCP server + webapp let you do.
 */

export interface AppEntry {
  label: string;
  url: string;
  port?: number;
  /** One sentence: what the app/tool actually is (for Joe normal user). */
  whatItIs: string;
  /** What you can do with the MCP server and webapp (short bullets or sentence). */
  whatYouCanDo: string;
}

export const APPS_CATALOG: AppEntry[] = [
  {
    label: "Calibre MCP",
    url: "http://127.0.0.1:10721",
    port: 10721,
    whatItIs: "This app. Manage your e-book library: search, metadata, full-text and semantic search, open books in your reader.",
    whatYouCanDo: "Browse books, search by keyword or by meaning (e.g. “book where someone was killed with an icicle”), switch libraries, export, chat with AI about your library.",
  },
  {
    label: "Blender",
    url: "http://127.0.0.1:10722",
    port: 10722,
    whatItIs: "Blender is a free, open-source 3D creation suite: modeling, animation, simulation, rendering, and compositing. Used for films, games, and 3D art.",
    whatYouCanDo: "Control Blender from the web or from AI: create and edit scenes, run scripts, render images. The MCP server talks to Blender so an assistant can help you build 3D projects.",
  },
  {
    label: "PlexMCP",
    url: "http://127.0.0.1:10741",
    port: 10741,
    whatItIs: "Plex is a media server for your movies, TV shows, and music. You host the files; Plex streams them to your devices.",
    whatYouCanDo: "Browse your Plex library, search, and control playback via the webapp and MCP. Ask an AI to “play something from my sci‑fi collection” or find a film.",
  },
  {
    label: "Advanced Memory",
    url: "http://127.0.0.1:10704",
    port: 10704,
    whatItIs: "A knowledge base that stores notes, research, and links in a graph. Think “second brain” for projects and learning.",
    whatYouCanDo: "Add and search notes, build context for AI conversations, export and sync. MCP tools let an assistant read and write your knowledge base.",
  },
  {
    label: "Robotics MCP",
    url: "http://127.0.0.1:10706",
    port: 10706,
    whatItIs: "Tools for robots and automation: control, status, and scripting for supported hardware (e.g. Unitree, other MCP‑compatible bots).",
    whatYouCanDo: "Monitor and control robots from the web or via AI. The MCP server exposes commands so an assistant can help you run or debug robot workflows.",
  },
  {
    label: "MyAI Dashboard",
    url: "http://127.0.0.1:3060",
    port: 3060,
    whatItIs: "Central dashboard for the MyAI microservices platform: chat, RAG, avatars, image generation, and more.",
    whatYouCanDo: "Start and stop services, check health, and open individual MyAI apps (Calibre Plus, Plex Plus, Document Viewer, etc.) from one place.",
  },
  {
    label: "Virtualization MCP",
    url: "http://127.0.0.1:10700",
    port: 10700,
    whatItIs: "Manage virtual machines (e.g. VirtualBox, Hyper-V): create, start, stop, and snapshot VMs.",
    whatYouCanDo: "List and control VMs from the web or via AI. Useful for dev environments, testing, or “spin up a Windows VM and install this stack.”",
  },
  {
    label: "Database Ops MCP",
    url: "http://127.0.0.1:10708",
    port: 10708,
    whatItIs: "Run and manage database operations (queries, migrations, backups) against configured databases.",
    whatYouCanDo: "Execute queries and common admin tasks from the web or through an AI assistant, with safety and logging.",
  },
  {
    label: "Avatar MCP",
    url: "http://127.0.0.1:10710",
    port: 10710,
    whatItIs: "Talking avatars and voice AI: generate or drive avatar videos and audio from text or chat.",
    whatYouCanDo: "Create avatar content and control playback via the webapp and MCP. Integrates with TTS and video pipelines.",
  },
  {
    label: "VRChat MCP",
    url: "http://127.0.0.1:10712",
    port: 10712,
    whatItIs: "VRChat is a social VR platform. This app connects it to MCP so you can query or control aspects from outside VR.",
    whatYouCanDo: "Use the web or an AI to interact with VRChat data and actions (worlds, friends, etc.) without putting on a headset for every lookup.",
  },
  {
    label: "Ring MCP",
    url: "http://127.0.0.1:10728",
    port: 10728,
    whatItIs: "Ring doorbells and cameras: view events, live streams, and device status.",
    whatYouCanDo: "Check who’s at the door, review recent events, and control Ring devices from the web or via an AI assistant.",
  },
  {
    label: "MyAI Calibre Plus",
    url: "http://127.0.0.1:10734",
    port: 10734,
    whatItIs: "Another Calibre-based library UI in the MyAI ecosystem, with its own features and integrations.",
    whatYouCanDo: "Browse and manage your e-books with a different workflow or UI than this Calibre MCP app; pick the one that fits you.",
  },
  {
    label: "MyAI Plex Plus",
    url: "http://127.0.0.1:10760",
    port: 10760,
    whatItIs: "Plex front-end in the MyAI stack: browse and play your Plex library with a custom UI.",
    whatYouCanDo: "Search and play Plex media; may offer different layout or features than the main Plex app or PlexMCP.",
  },
  {
    label: "Games App",
    url: "http://127.0.0.1:10726",
    port: 10726,
    whatItIs: "A hub for games: library, launches, and metadata. Manages your game collection across stores and platforms.",
    whatYouCanDo: "Browse games, see what’s installed, and launch them. MCP can help an AI suggest or open games from your library.",
  },
];
