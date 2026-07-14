"""Infrastructure monitoring subcommand (``leleka ps``).

Provides ``--pulse`` for project overview and ``--models`` for Ollama model listing.
"""

from __future__ import annotations

import typer
from rich.console import Console
from leleka.tools.ps_helpers import show_system_pulse, show_models

app = typer.Typer(help="System infrastructure monitoring")
console = Console()


@app.callback(invoke_without_command=True)
def ps_main(
    pulse: bool = typer.Option(False, "--pulse", help="Table of projects registered to system"),
    models: bool = typer.Option(False, "--models", help="Status about installed and running Ollama models."),
) -> None:
    """Handle ``leleka ps`` subcommand dispatch.

    Args:
        pulse: Show the project pulse table.
        models: List installed Ollama models.
    """
    if pulse:
        show_system_pulse()
    elif models:
        console.print("[bold magenta]🧠 Ollama Models Overview...[/bold magenta]")
        show_models()
    else:
        console.print("[yellow]Action 'ps' needs --pulse or --models.[/yellow]")