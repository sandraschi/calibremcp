# chunk_01: User-Provided Rulebooks in Windsurf IDE – Tips, Tricks, and Best Practices

## Introduction
This chunk explores how users create, manage, andeploy rulebooks in the Windsurf IDE and similar agentic environments. It includes community tips, best practices for placement, and strategies for maximizing the utility of rulebooks.

## Key Insights
- **User-Provided Rulebooks:**
  - Most users place theirulebooks in `docs/rules.md` for discoverability and convention.
  - Some advanced teams use `docs/meta-rules.md` forganization-wide policies, and `docs/flows/` for specialized flows (e.g., bug, research, onboarding).
  - Referencing rulebooks in the project README or onboardinguide is considered best practice.
- **Activation:**
  - Users typically enable rulebooks inew sessions by prompting: `Use docs/rules.md as the agentic rulebook for bug and research flows.`
  - Some teams automate this via projectemplates or pre-session scripts.
- **Tips & Tricks:**
  - Keep rulebooks concise, modular, and versioned.
  - Use clear token blocks (e.g., `bug: ... :bug` or `research: ... :research`) to trigger agentic flows.
  - Document meta-rules for multi-project or cross-team consistency.

## Best Placement
- **Project Root:** `docs/rules.md` for primary rulebook
- **Meta/Org Level:** `docs/meta-rules.md` or `docs/flows/rules.md`
- **Specialized Flows:** Subdirectories under `docs/flows/` (e.g., `docs/flows/bugs/`, `docs/flows/research/`)

## Next Chunk
- Examples of rulebooks found on the web and comparison tother agentic IDEs' handling of rules.
