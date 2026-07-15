"""CLI entry point for the Leleka assistant.

Subcommands::

    leleka run   Unified prompt / chat command (replaces ``ask`` and ``chat``)
    leleka ps    Infrastructure monitoring (--pulse, --models)

The legacy ``ask`` and ``chat`` commands are deprecated but kept as no-op stubs.
"""

from __future__ import annotations

import typer
from rich.console import Console
from leleka.commands import ask, chat, ps  # noqa: F401 — imported for deprecation stubs
from leleka import config
from leleka.commands.run import execute_run

app = typer.Typer(
    name="Leleka",
    help="[bold cyan] LELEKA CLI AI [bold cyan]",
    no_args_is_help=True,
    rich_markup_mode="rich"
)
console = Console()


@app.command("run", help="[cyan]Unified prompt / chat command[/cyan]")
def run_cmd(
    model: str = typer.Option(config.DEFAULT_MODEL, "--model", "-m"),
    no_stdin: bool = typer.Option(False, "--no-stdin", help="Force interactive mode even when stdin is detected."),
) -> None:
    """Run Leleka — interactive chat or one-shot prompt from piped text.

    Args:
        model: Ollama model identifier (default from config).
        no_stdin: Skip stdin detection; always enter interactive mode.
    """
    execute_run(model=model, no_stdin=no_stdin)


@app.command("ask")
def _deprecated_ask(
    prompt: str = typer.Argument(..., help="Prompt text"),
) -> None:
    """Deprecated *ask* command — prints a warning and exits."""
    console.print("[yellow][DEPRECATED][/yellow] 'ask' is deprecated. Use '[bold]leleka run[/bold]' instead.")
    raise typer.Exit()


@app.command("chat")
def _deprecated_chat() -> None:
    """Deprecated *chat* command — prints a warning and exits."""
    console.print("[yellow][DEPRECATED][/yellow] 'chat' is deprecated. Use '[bold]leleka run[/bold]' instead.")
    raise typer.Exit()

app.add_typer(ps.app, name="ps", help="[magenta]Infrastructure monitoring.[/magenta]")

if __name__ == "__main__":
    app()
