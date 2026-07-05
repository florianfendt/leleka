**Objective:** Implement a unified `leleka` CLI engine that collapses historical script fragments into a high-density, multi-functional single-file command monolith powered by **UV Script Metadata** and **Typer**[cite: 4]. This architecture absorbs configuration resolution and deprecates legacy code by delegating structural actions under explicit, context-aware command boundaries (`ask`, `chat`, `ctx`).

> **Instructions for Local Models:** Execute this plan sequentially, **one subtask per session**. Do not attempt multiple subtasks at once. Check off `[ ]` items only when fully functional, thoroughly documented with comprehensive architecture docblocks, and verified locally.

---

## 🏗️ Phase 1: Core CLI Engine & Spiderweb Integration
**Session Focus:** Unified monolith setup, initialization parameters, and global configuration mapping.

*   [ ] **Subtask 1.1: UV Script Metadata & Unified CLI Architecture**
    *   Create the primary monolithic execution file `leleka.py` with embedded inline `uv` script dependency headers declaring requirements for `typer`, `rich`, `ollama`, and `langchain-core`[cite: 2, 3, 4].
    *   Set up a unified `typer.Typer()` command layout that acts as the sole access terminal point[cite: 4].
    *   Map the three primary structural operational modes: `leleka ask`, `leleka chat`, and `leleka ctx`.
*   [ ] **Subtask 1.2: Spiderweb Dynamic Configuration Resolver**
    *   Absorb configuration handling directly into the script execution scope by reading configuration parameters from `~/.config/spiderweb/config.toml` or `paths.json` dynamically[cite: 1].
    *   Establish explicit absolute filesystem fallbacks for critical system paths (`ROLES`, `PROJECTS`, `CONTEXT` keys) via `.expanduser().resolve()` mappings[cite: 1].
    *   Migrate legacy infrastructure components (e.g., the `switanok` command and its related hardcoded MAC addresses) to a dedicated archive script `utils/legacy.py`[cite: 6].

---

## 💬 Phase 2: Execution Channels (`ask` & `chat`)
**Session Focus:** Preserving stable agent streaming routes while adding multi-turn capabilities.

*   [ ] **Subtask 2.1: Protected `ask` Command Porting**
    *   Port the existing prompt routing logic from `ai_commands.py` directly into the unified monolith without modifying the core functional text logic[cite: 4].
    *   Ensure proper structural loading of role manifesto configurations and conditional structural project blueprint attachments via `PROJECTS` markdown lookups[cite: 4].
    *   Connect the formatted prompt strings to the inline execution stream using the `stream_leleka_response` interface driver[cite: 4].
*   [ ] **Subtask 2.2: Stateful Multi-Turn `chat` Engine**
    *   Implement an interactive, infinite loop execution channel (`leleka chat`) within the terminal space using standard input prompts.
    *   Maintain an in-memory session history array that appends alternating user strings and corresponding assistant returns to track deep multi-turn systemic interactions.
    *   Integrate real-time chunk token rendering using the optimized streaming display loops inside the console panels[cite: 3].

---

## 📂 Phase 3: High-Density Context Operations (`ctx`)
**Session Focus:** Code structural collapse, file traversal engines, and categorical workspace analysis.

*   [ ] **Subtask 3.1: Directory Tree Structural Collapse (`--collapse`)**
    *   Design a file traversal method under `leleka ctx` that takes a targeted workspace directory path argument.
    *   Recursively scan the targeted path, read all discovered content files (utilizing the internal logic of `load_context_file_content` and code-stripping boundaries), and output a single, consolidated Markdown document containing clear visual structure divisions[cite: 2].
*   [ ] **Subtask 3.2: Multidimensional Metadata Slicing (`--categorize`)**
    *   Incorporate flexible sorting routines modeled after the historical `LocalContextEngine.filter_and_categorize` framework[cite: 2].
    *   Provide explicit sorting options to group parsed context variables in different arrangements, including grouping documents by file extension formats, system folder tiers, or time-based metrics[cite: 2].
*   [ ] **Subtask 3.3: Historical Archive Consolidation**
    *   Isolate all legacy framework elements that are no longer actively mapped to active CLI execution trees (such as old subroutines or specialized subprocess triggers)[cite: 5, 6].
    *   Move these components to `utils/legacy.py` to keep the primary `leleka.py` codebase highly focused, cohesive, and easily auditable.