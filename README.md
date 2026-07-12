# leleka

**Lightweight local-first AI assistant CLI — powered by Ollama.**

Leleka brings the power of large language models to your terminal with zero cloud dependency. Run queries, hold conversations, and monitor your system health — all from a single command-line tool backed by your local Ollama instance.

> The Stork is watching...

## Features

- **One-shot prompts** — fire off a question with optional file context and get live-streamed responses
- **Persistent chat sessions** — multi-turn conversations saved as markdown files for later reference
- **System monitoring** — list local Ollama models, inspect system pulse events
- **Project scaffolding** — structured Markdown documents with templated chapters
- **Workspace helpers** — scrape context from CSV, JSON, and code files into LLM-ready format

## Installation

### From source

```bash
git clone https://github.com/<user>/leleka.git
cd leleka
uv pip install -e .
```

### Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `typer` | >= 0.12 | CLI framework |
| `rich` | >= 13 | Live streaming panels & tables |
| `ollama` | >= 0.3 | Local LLM backend |

Ollama must be installed and running locally with at least one model pulled (e.g. `mistral:7b`).

## Usage

```bash
# One-shot prompt (with optional file context)
leleka ask "What do you think about this?" --file analysis.csv

# Interactive chat session (history saved automatically)
leleka chat

# System monitoring
leleka ps --models          # list local Ollama models
leleka ps --pulse           # display system pulse data
```

### Environment variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `CONTEXT_PATH` | Directory for context files | project root /context |
| `CHATS_PATH` | Directory for saved chat sessions | project root /chats |
| `MODELS_PATH` | Directory for model system prompts | project root /models |

## Architecture

```
leleka/
├── main.py              # CLI entry point — wires sub-apps together
├── config.py            # Path constants, defaults, logo text
├── core/
│   ├── llm.py           # Streaming engine (ollama.chat + Rich Panel)
│   └── projects_engine.py  # Markdown section dataclass (ProjectFile)
├── commands/
│   ├── ask.py           # One-shot prompt command
│   ├── chat.py          # Interactive REPL chat command
│   └── ps.py            # System monitoring command
└── tools/
    ├── projects_helpers.py  # Project scaffolding utilities
    ├── ps_helpers.py        # Ollama model listing, pulse display
    └── workspace_ops.py     # CSV↔MD conversion, context scraping
```

## Roadmap

- [ ] Unify `ask` + `chat` into a single command with mode flags
- [ ] Provider abstraction layer (swap Ollama for other backends)
- [ ] Type hints, docstrings, and test coverage
- [ ] Restore missing `.markdown_utils` submodule

## License

[To be determined]
