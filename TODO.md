# leleka - TODO

- [x] #03: Unify `ask` + `chat` into one command (`leleka run`) with stdin piping support → created `commands/run.py`, `tools/session_ops.py`; deprecated old aliases in `main.py`
- [ ] #04: Add Ollama abstraction layer (provider interface) to enable swapping backends without touching multiple files
- [ ] #06: Add type hints, docstrings, and tests (current code violates CLAUDE.md guardrails on all three)
