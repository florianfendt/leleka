# leleka - TODO

- #03: Unify `ask` + `chat` into one command with `--chat` / `--prompt` options (`--chat` default) → refactor `commands/chat.py`, `commands/ask.py`, update `main.py` wiring
- #04: Add Ollama abstraction layer (provider interface) to enable swapping backends without touching multiple files
- #06: Add type hints, docstrings, and tests (current code violates CLAUDE.md guardrails on all three)
