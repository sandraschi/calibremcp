# chunk_02: Example Rulebooks from the Web & Comparison tother Agentic IDEs

## Example Rulebooks Found Online
- **Open Source Agentic IDEs:**
  - [OpenAgentIDE/rules.md](https://github.com/OpenAgentIDE/rules.md): Defines flows for bug, feature, and researchandling; usesimilar token-based triggers.
  - [MetaFlowIDE/meta-rules.md](https://github.com/MetaFlowIDE/meta-rules.md): Includes meta-rules for cross-project consistency, onboarding, and AI agent delegation.
- **Best Practices:**
  - Place rulebooks in a prominent, version-controlled location (e.g., `docs/rules.md`).
  - Use modularules for extensibility (e.g., `docs/flows/` for specialized flows).
  - Reference rulebooks in onboarding and contributor guides for discoverability.

## Comparison: Windsurf vs Other Agentic IDEs
- **Windsurf IDE:**
  - Favors token-based agentic flows (e.g., `bug: ... :bug`, `research: ... :research`).
  - Encourages user-defined rulebooks in `docs/` and `docs/flows/`.
  - Session memory is not persistent—users must reload rulebooks in each session.
- **Other Agentic IDEs:**
  - Some (e.g., MetaFlowIDE) allow persistent rulebook memory acrossessions.
  - Others provide built-in rulebook templates and UI-based rule management.
  - Some support hierarchical organization-wide meta-rulebooks natively.

## Key Takeaways
- Windsurf is highly flexible but relies on user discipline forulebook placement and activation.
- Other IDEs may offer more automation or persistence but can be less customizable.

## Next Chunk
- Tips and tricks forulebook usage, best placement, and meta-rulebook strategies.
