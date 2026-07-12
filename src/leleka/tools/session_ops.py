"""Shared session helpers for the unified ``run`` command.

Extracts common logic from ``commands/ask.py`` and ``commands/chat.py``:
system-prompt loading, streaming panel rendering, and token-stats display.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterator

from leleka import config
from leleka.tools.projects_helpers import calc_token_stats, show_context_stats
from rich.console import Console
from rich.live import Live
from rich.panel import Panel


console = Console()


def load_system_prompt(model: str) -> str | None:
    """Load the system prompt for *model* from ``MODELS_PATH``.

    Returns ``None`` when no matching model file exists.
    """
    model_file = config.MODELS_PATH / f"{model}.md"
    if model_file.exists():
        return model_file.read_text(encoding="utf-8")
    return None


def render_stream(
    *,
    title: str,
    border_style: str = "cyan",
) -> Iterator[tuple[Live, Panel]]:
    """Context-manager that yields a Rich ``Live`` + ``Panel`` for streaming.

    Usage::

        with render_stream(title="Leleka (mistral:7b)") as (live, panel):
            live.update(panel)  # call after each chunk update
    """
    with Live(
        Panel("", title=title, border_style=border_style),
        console=console,
    ) as live:
        yield live, live.console


def show_token_stats_from_chunk(chunk: dict) -> None:
    """Display token-usage stats from an Ollama *chunk* dictionary."""
    stats = calc_token_stats(chunk)
    show_context_stats(stats)


def read_stdin_if_available() -> str | None:
    """Read all of stdin when it is **not** a TTY (piped input).

    Returns the piped text, or ``None`` when nothing was piped.
    """
    if not sys.stdin.isatty():
        return sys.stdin.read()
    return None
