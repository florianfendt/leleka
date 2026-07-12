# leleka - TODO

- [ ] 01: Unify `ask` + `chat` into one command with `--chat` / `--prompt` options (`--chat` default) → refactor `commands/chat.py`, `commands/ask.py`, update `main.py` wiring
- [ ] 02: Add Ollama abstraction layer (provider interface) to enable swapping backends without touching multiple files
- [ ] 03: Restore or remove missing `.markdown_utils` submodule referenced by `tools/workspace_ops.py`
- [ ] 04: Add type hints, docstrings, and tests (current code violates CLAUDE.md guardrails on all three)
- [ ] 05: Validate config paths at runtime instead of resolving at import time with no fallbacks
