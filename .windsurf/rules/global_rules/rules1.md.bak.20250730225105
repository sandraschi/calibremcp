---
trigger: always_on
---

# SandrasRules (Global Rulebook)

This is the canonical, protected global rulebook for all Windsurf/Cascade agentic workflows, named "SandrasRules" per user preference.

## Rule to prove this was actually read
- Add “lgr1 “ to casade outputs

## Change Management and User Consent
- Never remove, rewrite, or break major functionality (such as backend support, critical features, or user workflows) without explicit user instruction.
- Always clarify and confirm with the user before making any change that would break, remove, or replace existing features, especially if it could disrupt workflows or compatibility.
- Clearly summarize any impactful or potentially breaking changes before applying them. If there is any ambiguity, ask the user for approval.
- Provide explicit diffs and summaries for all major edits so the user can review before anything is lost.
- If the user specifies workflow or safety preferences (e.g., always prompt before deleting code, or require a summary of changes before applying), these must be strictly followed.
- If possible, offer to help set up lightweight, auto-staged commits or other safety nets to prevent accidental loss of work and make rollbacks easy.

## Agentic Bug report and Research Handling Rules

### 1. Bug Handling (`bug: ... :bug`)
- Use the token `bug:` to start a bug description, and `:bug` to end it.
- When a bug block is encountered:
  1. Research the bug thoroughly.
  2. Place the bug description and your analysis in two separate files, in a new directory under `/.windsurf/docs/flows/bugs/`.
     - Directory name format: `YYMMDD_short-description` (current date and concise bug name).
     - Example files: `bug.md` (original bug description), `analysis.md` (your analysis and findings).
  3. Follow the structure of existing entries in `/.winsurf/docs/flows/bugs/` for formatting and organization.

### 2. Research Handling (`research: ... :research`)
- Use the token `research:` to start a research request, and `:research` to end it.
- When a research block is encountered:
  1. Research the topic as thoroughly as possible. 300 öines optimal
  2. Place the research results in a new subdirectory under /.windsurf/docs/flows/research/.
     - Directory name format: `YYMMDD_short-topic` (current date and concise topic name).
     - Research results should be split into multiple markdown files named `chunk_01.md`, `chunk_02.md`, etc.
     - Follow the formatting, structure, and depth of existing research entries in /docs/flows/research/.
  3. Each `chunk_XX.md` should be well-structured, with clear sections and references as needed.

**Note:**
- Always follow these rules when encountering the specified tokens in prompts or files.
- If you are unsure of the structure, refer to existing examples for bugs and research in their respective directories.
- These rules are mandatory for all agentic coding, bug, and research workflows in Windsurf/Cascade.
- They are designed to maximize user control, transparency, and project safety.

### 3. Links and Other Flows
- For other tokens such as `links:` or `:links`, or analogous flows, consult the structure and rules in the `/.winsurf/docs/flows/` directory and follow their conventions.

## Filesystem Safety and Directory Creation
- Never try to edit or create a file in a nonexistent directory.
- Always check if the target directory exists before file operations.
- If the directory does not exist, create it first using PowerShell's `New-Item -ItemType Directory -Force`.
- This rule applies to all agentic and automated workflows, including bug and research flows.

## Script syntax
- Never use linux syntax in windows shells, batch scripts or cascade commands
- No rmdir, mkdir or cd with linux-style parameters
- No && for chaining commands, use semicolon

---

## Robustness, Logging, and File Management

- **Comprehensive Error Handling:**
  - All code, scripts, and agentic actions must implement robust error handling.
  - Catch and handle exceptions at logical boundaries; never silently ignore errors.
  - Use logger service, not console
  - Always provide clear, actionable error messages and fail safely, informing the user.

- **Robust Logging:**
  - Log all critical operations, decisions, and errors with timestamps and context.
  - Use the logger service, not console commands (e.g.logger.error instead of console.error)
  - Never log sensitive data (e.g., passwords, API keys).
  - Ensure logs are easy to locate, search, and rotate.

- **User Notification of Failures:**
  - Always notify the user of errors or unexpected events, with a clear summary and suggested next steps.

- **Automated Backups:**
  - Before destructive or high-impact operations, create a backup or checkpoint.
  - Inform the user where the backup is stored and how to restore it.

- **Code and Data Provenance:**
  - Record the origin, version, and timestamp of imported code, data, or rulebooks.
  - Log all rulebook merges, imports, or significant changes.

- **Security and Privacy:**
  - Never log, display, or transmit sensitive information unless explicitly required and approved.
  - Always sanitize user input and validate external data sources.

- **Transparency and Explainability:**
  - For every automated or agentic action, provide a summary of what was done, why, and what rules or logic were followed.
  - Allow the user to request a full activity or decision log at any time.

- **File Size and Editability:**
  - Avoid creating or maintaining source files so large that they cannot be safely or atomically edited by Cascade or similar tools.
  - When a file approaches the system's edit or memory limits, proactively split it into smaller, logical modules or use chunked editing strategies.
  - Never attempt a single edit operation on a file that risks failure due to size; always prefer modularity and maintainability.

---

## Autonomous/Multi-Step Macros and Protections

- **streakXX:**
  - Use the macro `streakXX:` (where XX is a positive integer) to instruct Cascade to perform up to XX safe, autonomous steps without user intervention.
  - Example: `streak20: make pacman subproject` will attempt up to 20 safe, non-dangerous steps to implement the requested feature.
- **Protections and Limits:**
  - Enforce a hard cap on steps (XX), time (e.g., 10 minutes), and estimated cost.
  - Limit automatic retries on failed edits or commands to 2 attempts per operation.
  - If the same operation fails more tha

---

## File Size and Modular Architecture Rules

### **MANDATORY FILE SIZE LIMITS**
Never create files longer than these limits without modular refactoring:

- **JavaScript/TypeScript**: 300 lines max (optimal: 150-250)
- **HTML**: 400 lines max (optimal: 200-300)  
- **CSS**: 500 lines max (optimal: 250-400)
- **Documentation**: 800 lines max (optimal: 400-600)
- **Configuration/Data Files (JSON/YAML)**: 150 lines max (optimal: 50-100)

### **Pre-Writing Process**
1. **Estimate Line Count** - Before starting any file, estimate final size
2. **Check Against Limits** - Compare estimate with file type limits above
3. **Plan Modular Structure** - If exceeding limits, plan folder structure first
4. **Announce Refactoring** - Tell user: "This will be >X lines, creating modular structure instead"

### **Modular Refactoring Patterns**

#### **JavaScript/TypeScript Libraries (>300 lines):**
```
my-library/
├── index.js                 # Main export file (~50-80 lines)
├── README.md               # Documentation
└── src/
    ├── core.js             # Core functionality (~200-250 lines)
    ├── utils.js            # Utility functions (~150-200 lines)
    ├── api.js              # API interactions (~200-250 lines)
    └── components.js       # UI components (~200-250 lines)
```

#### **Complex Applications (>300 lines):**
```
my-app/
├── index.js                # Entry point (~80-100 lines)
├── config.js              # Configuration (~100-150 lines)
├── README.md              # Documentation
└── modules/
    ├── auth.js            # Authentication (~200-250 lines)
    ├── ui.js              # User interface (~250-300 lines)
    ├── data.js            # Data management (~200-250 lines)
    └── api.js             # API calls (~150-200 lines)
```

#### **HTML Applications (>400 lines):**
```
my-page/
├── index.html             # Main structure (~150-200 lines)
├── components/
│   ├── header.html        # Header component (~80-120 lines)
│   ├── navigation.html    # Navigation (~100-150 lines)
│   ├── main-content.html  # Main content (~200-300 lines)
│   └── footer.html        # Footer component (~60-100 lines)
└── assets/
    ├── styles/
    │   ├── main.css       # Main styles (~300-400 lines)
    │   ├── components.css # Component styles (~250-350 lines)
    │   └── responsive.css # Media queries (~200-300 lines)
    └── scripts/
        ├── main.js        # Main functionality (~250-300 lines)
        ├── components.js  # Component logic (~200-250 lines)
        └── utils.js       # Utilities (~150-200 lines)
```

### **Implementation Workflow**
1. **Stop Before Exceeding** - If file will exceed limits, STOP immediately
2. **Create Folder Structure** - Set up logical directory structure
3. **Write Focused Modules** - Each file should have single responsibility
4. **Create Index/Main** - Entry point that imports/exports modules
5. **Document Structure** - Create README explaining architecture
6. **Use Clear Names** - File names should describe exact purpose

### **Benefits of Modular Architecture**
- **Performance**: Smaller files load and parse faster
- **Debugging**: Issues isolated to specific modules
- **Maintenance**: Easier to update specific functionality
- **Collaboration**: Multiple developers can work on different modules
- **Testing**: Components can be tested in isolation
- **Reusability**: Modules can be reused across projects

### **Exception Handling**
Large files are acceptable only for:
- Auto-generated code (document this clearly)
- Large datasets (consider database instead)
- Legacy integration (refactor when possible)
- Third-party libraries (don't modify)

**Must be explicitly justified with refactoring plan and timeline.**

### **Monitoring and Enforcement**
- Check file size every 100 lines during writing
- Stop at 80% of limit to plan refactoring
- Single responsibility per file
- Logical grouping of related functions
- Clear naming conventions

**GOLDEN RULE: "If you're thinking about writing a file longer than these limits, think modular instead!"**

This prevents truncated files, unmanageable code, debugging nightmares, and promotes clean, professional architecture.

