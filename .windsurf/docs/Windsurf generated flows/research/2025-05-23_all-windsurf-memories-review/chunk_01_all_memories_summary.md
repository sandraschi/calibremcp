# Researchunk 01: Summary of All Provided Windsurf Memories

Date: 2025-05-23

This document provides a condensed summary of all memories provided by the USER, extracted from the Windsurf system. Each memory is listed with its identifier and a brief overview of its content.

## Global Rules & Agent Behavior

### 1. MEMORY[user_global] - SandrasRules (Global Rulebook)
*   **Content Summary:** This the canonical, protected global rulebook for Windsurf/Cascade agentic workflows.
    *   **Change Management:** Emphasizes user consent for major changes, requiring clarification, summaries, and explicit diffs. Suggestsafety nets like auto-staged commits.
    *   **Agentic Bug/Researchandling:** Defines procedures for `bug: ... :bug` and `research: ... :research` tokens, including directory structures (`docs/flows/bugs/YYYY-MM-DD...`, `docs/flows/research/YYYY-MM-DD...`) and file naming conventions (`bug.md`, `analysis.md`, `chunk_XX.md`).
    *   **Filesystem Safety:** Mandates checking for directory existence before file operations and creating directories if non-existent using PowerShell's `New-Item -ItemType Directory -Force`.
    *   **Robustness & Logging:** Requires comprehensiverror handling, robust logging (no sensitive data), user notification ofailures, automated backups before destructive operations, code/data provenance, and security/privacy measures.
    *   **Transparency & Explainability:** Agent actionshould be summarized with reasoning.
    *   **File Size & Editability:** Avoid overly large source files; prefer modularity or chunkediting.
    *   **Autonomous Macros (`streakXX`):** Allows Cascade to perform up to XX safe, autonomousteps, with limits on steps, time, and cost. Includes rules foretry limits on failed operations.

### 2. MEMORY[dont-apologize.md]
*   **Content Summary:** A direct instruction for Cascade to never apologize, as it's perceived as annoying and insincere.

### 3. MEMORY[sandras-rules.md]
*   **Content Summary:** This appears to be a very similar, if not identical, version of `MEMORY[user_global]`, reiterating SandrasRules. It covers:
    *   Change Management and User Consent.
    *   Agentic Bug and Researchandling (`bug:`, `research:`, `links:` tokens) with specific directory structures (`/docs/flows/bugs/YYMMDD...`, `/docs/flows/research/YYMMDD...`).
    *   Filesystem Safety (directory creation with PowerShell).
    *   Robustness, Logging, and File Management (error handling, logging, user notification, backups, provenance, security, transparency, file size limits).
    *   Autonomous/Multi-Step Macros (`streakXX`) with protections and limits.

### 4. MEMORY[da9f5542-f005-4406-9bc6-6acc3fb7bc8b] - Cascade Bug: Empty Tool Code Block
*   **Content Summary:** User pointed out a formatting error where Cascade included empty `<tool_code_block>\n\n</tool_code_block>` tags. Thishould be avoided.

### 5. MEMORY[47386bee-85b0-42e6-982f-ca895cef4051] - Cascade Proactivity
*   **Content Summary:** Cascade should proactively perform actions it's capable of using its tools, rather than asking the user to do them, while still adhering to safety protocols for potentially destructive operations.

### 6. MEMORY[fde90bd6-9ceb-4602-b599-e83d67a97dc3] - Code Change Workflow
*   **Content Summary:** Defines a clear workflow for code changes: 1) Show proposed changes. 2) Indicate review vs. application. 3) Apply only after explicit user confirmation. 4) Make proposals visually distinct. 5) Confirm applied changes with a summary.

## Technical Discussions & Solutions

### 7. MEMORY[330b9a1d-3aaa-4e2f-a261-ad379b9bc7e5] - Anthropic API, BYOK, Cascade Issues
*   **Content Summary:** Discussed Anthropic API pricing (Opus 4, Sonnet 4, Haiku 3.5) and Windsurf's 'Bring Your Own Key' (BYOK) for these models due to no direct Claude 4 access. BYOK was found 'complicated' by users. Also mentions Cascade bugs (empty tool tags) and lack of persistenthought process view or direct chat export in Windsurf.

### 8. MEMORY[50b45f0d-0167-489f-8f08-df7c38d2ef69] - Minimal Dockerized React App Success
*   **Content Summary:** Achieved successful display of 'Hello World' from a minimal React (TypeScript) app, built with esbuild, served via Nginx, all in Docker. Key fixes involved React DOM rendering target and JS bundle path.

### 9. MEMORY[0bcb64d8-1b6b-42ca-85da-9db2fbdc5ada] - TypeScript/Reactypes Resolution
*   **Content Summary:** Identified and fixed widespread TypeScript errors (missing React namespacexports) by updating `@types/react` (to `18.2.79`) and `@types/react-dom` (to `18.2.25`) in `calibre_plus/frontend/package.json`. Advisedeleting `pnpm-lock.yaml` and rebuilding Docker image.

### 10. MEMORY[8efde1d8-7b1e-4526-9654-91af91ef702d] - Principles for Dockerized React (TS) App
*   **Content Summary:** Outlines key principles for building a Dockerized React (TypeScript) app with esbuild and Nginx:
    1.  `package.json` build script (`tsc && esbuild`).
    2.  `src/index.tsx` rendering to an existing DOM element.
    3.  `index.html` script reference to the bundled JS.
    4.  Multi-stage `Dockerfile` (build stage with Node, production stage with Nginx).
    5.  `tsconfig.json` settings (`jsx`, `module`, `moduleResolution`, `lib`).

### 11. MEMORY[a436fcea-e3af-4774-94ed-e3ba828b9735] - Calibre++ Deployment Setup
*   **Content Summary:** Details the setup for the Calibre++ application, including Docker (`docker-compose.yml`), Waitress (backend), Nginx (frontend), Coolify deployment (`coolify.json`), and various helper scripts (`run_dev.ps1/sh`, `docker-run.ps1/sh`, etc.). Application is ready for deployment with semantic search and RAG.

### 12. MEMORY[2df545ea-e611-432d-8b9b-d219a1e5f5d0] - Plex++ RAG with ChromaDB
*   **Content Summary:** User intends to implement Retrieval-Augmented Generation (RAG) in the Plex++ application using ChromaDB as the vector database.

## System Operations & Best Practices

### 13. MEMORY[10b6badb-bb45-45cd-aaf5-28e31e8f11fb] - Docker Port Allocation Management
*   **Content Summary:** Guideline for managing Docker port conflicts: list running containers, stop conflicting ones, and retry. Use `--rm` flag with `dockerun`.

### 14. MEMORY[3a135e1d-1fc9-4637-9dad-21292617af03] - Process Management Best Practices
*   **Content Summary:** Rules for process management:
    1.  Always use non-blocking process termination.
    2.  Windows: `start /B taskkill /F /IM process.exe`.
    3.  Cross-platform: Python's `subprocess.Popen` with `creationflags=subprocess.CREATE_NEW_PROCESS_GROUP` (Windows).
    4.  Never use blocking commands without user confirmation.
    5.  Use built-in shutdown endpoints for dev servers when possible.

### 15. MEMORY[88dffc3a-2bbe-4ef1-90f4-a265cdbd0fca] - Non-Blocking System Operations
*   **Content Summary:** Emphasizes preferring non-blocking methods for system operations (process management, file system ops, directory ops) to prevent UI freezes. Listspecific non-blocking approaches (e.g., `taskkill /F /IM process.exe` with `unref()`, `fs.promises`). Definesafety exceptions where blocking is allowed (e.g., critical system ops, userequest). Stresses error handling and memory management.

### 16. MEMORY[32cf7875-8fd3-4230-a098-406d331698b4] - Handling Long Terminal Outputs
*   **Content Summary:** For commands with potentially long terminal outputs (especially error logs), redirect `stdout` and `stderr` to a log file (e.g., `command > logfile.txt 2>&1`) and analyze the file, rather than relying on possibly truncated terminal scrollback.

### 17. MEMORY[037d098c-46f9-42ef-9bfc-4affefb75f2a] - Non-Blocking PowerShell Processes
*   **Content Summary:** Always use non-blocking process operations in PowerShell by default. Examples:
    *   Use `Start-Process` instead of direct command execution.
    *   Never use blocking `taskkill`.
    *   Run server processes with `-NoNewWindow` and `-PassThru`.
    *   Example: `Start-Process -NoNewWindow -FilePath "taskkill" -ArgumentList "/F /IM process.exe"`.

This compilation provides a comprehensive overview of the guidance, technical solutions, and user preferences captured in the provided memories.
