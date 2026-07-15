"""Legacy ``ask`` subcommand — deprecated in favour of ``run``.

Kept as a no-op stub that prints a deprecation warning.
"""

from __future__ import annotations

import os  # noqa: F401 — kept for compatibility
import typer
import ollama  # noqa: F401 — imported for deprecation stubs
from pathlib import Path
from rich.live import Live
from rich.panel import Panel
from rich.console import Console

from leleka import config
from leleka.tools import ps_helpers


app = typer.Typer()
console = Console()


@app.command("ask")
def ask_cmd(
    prompt: str = typer.Argument(..., help="Prompt text"),
    model: str = typer.Option("gemma4:12b", "--model", "-m"),
    file: Path | None = typer.Option(None, "--file", "-f"),
) -> None:
    """Deprecated *ask* command — prints a warning and exits.

    Args:
        prompt: User's prompt text (unused; kept for CLI compatibility).
        model: Ollama model identifier (unused; kept for CLI compatibility).
        file: Optional context file path (unused; kept for CLI compatibility).
    """
    console.print("[yellow][DEPRECATED][/yellow] 'ask' is deprecated. Use '[bold]leleka run[/bold]' instead.")
    raise typer.Exit()