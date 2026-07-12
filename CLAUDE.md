# leleka — CLI AI assistant (Ollama-focused)

## Structure (13 .py files, ~705 lines)

| Module | Purpose |
|--------|---------|
| `main.py` | Typer entry point → wires `ask`, `chat`, `ps` sub-apps |
| `config.py` | Path constants from env vars, DEFAULT_MODEL="mistral:7b", logo text |
| `core/llm.py` | Streaming engine — `ollama.chat(stream=True)` + Rich Panel |
| `core/projects_engine.py` | `ProjectFile`: markdown→sections dataclass (CRUD chapters) |
| `commands/ask.py` | One-shot prompt → `ollama.generate()` with optional file context |
| `commands/chat.py` | REPL chat loop, saves history to `{CHATS_PATH}/chat_{ts}_{model}.md` |
| `commands/ps.py` | Infra monitoring: `--pulse`, `--models` (Ollama CLI) |
| `tools/projects_helpers.py` | Scaffolding helpers using `ProjectFile` + token stats display |
| `tools/ps_helpers.py` | Ollama model listing, pulse display, logo rendering (227 lines — largest file) |
| `tools/workspace_ops.py` | CSV↔MD conversion, context scraping from files, dir sync |

## Key facts
- **No abstraction over Ollama** — providers hard-coded in 3 places (`core/llm.py`, `commands/ask.py`, `tools/ps_helpers.py`)
- `.markdown_utils` submodule referenced by `workspace_ops.py` is missing (broken import)
- Three empty `__init__.py` files (namespace markers only)

## TODO → see TODO.md
