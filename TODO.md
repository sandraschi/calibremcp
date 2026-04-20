# calibre-mcp — Implementation TODO

**Canonical tracker:** `D:\Dev\repos\mcp-central-docs\projects\calibre-mcp\TODO.md`
(mirrored here for convenience).

This file tracks implementation progress on roadmap projects. Each has a
full spec at `docs/plans/{PROJECT}.md` and an Agent Skill at
`.cursor/skills/calibre-mcp-{project}/SKILL.md` for AI-assisted building.

## At a glance

| # | Project              | Status      | Effort | Branch               |
|---|----------------------|-------------|--------|----------------------|
| 1 | Reading flow         | ⬜ not started | 2–3 d  | `feat/reading-flow`  |
| 2 | Annotations          | ⬜ not started | 3–4 d  | `feat/annotations`   |
| 3 | Book of the day      | ⬜ not started | 1 d    | `feat/botd`          |
| 4 | Duplicate detection  | ⬜ not started | 1–2 d  | `feat/dupes`         |
| 5 | Audiobook generator  | ⬜ not started | 5–7 d  | `feat/audiobook`     |

## How to start a project

```powershell
# Pick a project, e.g. reading flow
cd D:\Dev\repos\calibre-mcp
git checkout -b feat/reading-flow

# Read the spec
cat docs\plans\READING_FLOW_INTEGRATION.md

# Then in Cursor (or Claude Code, or Antigravity):
# > "Implement the reading-flow integration per the spec"
# The Agent Skill for this project loads automatically.
```

## Phase-level checklists

See the canonical tracker at
`D:\Dev\repos\mcp-central-docs\projects\calibre-mcp\TODO.md` for the
full phase-by-phase breakdown per project.

## Shipping a project

Each Agent Skill ends with an "Update on completion" section. Follow it:

1. Merge feature branch to master
2. Update `CHANGELOG.md` with new version entry
3. Bump version in `pyproject.toml` and `calibre_plugin/__init__.py`
4. Mark ✅ shipped in this TODO
5. Mark ✅ shipped in `docs/plans/README.md`
6. Update `D:\Dev\repos\mcp-central-docs\projects\FLEET_INDEX.md`
7. Update `D:\Dev\repos\mcp-central-docs\projects\calibre-mcp\TODO.md`
8. Add a dated `## Shipped` header at the top of the project spec
   (`docs/plans/{PROJECT}.md`)

---

*Roadmap and specs by Claude Opus 4.7 (Anthropic), April 2026.*
