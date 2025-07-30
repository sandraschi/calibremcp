# Agenticoding Rules: Bug and Research Tokens

## 1. Bug Handling Rules (`bug: ... :bug`)
- The token `bug:` starts a bug description, and `:bug` ends it.
- When a bug block is encountered:
  1. You must research the bug (whatever it is) thoroughly.
  2. Place the bug description and your analysis in two separate files, in a new directory under `docs/flows/bugs/`.
     - Directory name format: `YYYY-MM-DD_short-description` (use the current date and a concise bug name).
     - Example files: `bug.md` (the original bug description), `analysis.md` (your analysis and findings).
  3. Follow the structure of existing entries in `docs/flows/bugs/` formatting and organization.

## 2. Researchandling Rules (`research: ... :research`)
- The token `research:` starts a research request, and `:research` ends it.
- When a research block is encountered:
  1. Research the topic as thoroughly as possible.
  2. Place the research results in a new subdirectory under `docs/flows/research/`. (If this directory does not exist, create it.)
     - Directory name format: `YYYY-MM-DD_short-topic` (use the current date and a concise topic name).
     - Research resultshould be split into multiple markdown files named `chunk_01.md`, `chunk_02.md`, etc.
     - Follow the formatting, structure, andepth of existing research entries in `docs/research/` (currently misplaced, buto be used as examples).
  3. Each `chunk_XX.md` should be well-structured, with clear sections and references as needed.

## 3. Links and Other Flows
- For other tokensuch as `links:` or `:links`, or analogous flows, consulthe structure and rules in the `docs/flows/` directory and follow their conventions.

---

**Note:**
- Always follow these rules whencountering the specified tokens in prompts or files.
- If you are unsure of the structure, refer to existing examples for bugs and research in theirespective directories.
- These rules are mandatory for all future work involving bug and research tokens.
