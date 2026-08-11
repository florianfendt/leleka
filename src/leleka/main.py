# leleka/main.py

from __future__ import annotations

import typer
from leleka.commands import ps
from leleka.config import _cfg
from leleka.commands.run import execute_run

app = typer.Typer(
    name="Leleka",
    help="[bold cyan] LELEKA CLI AGENT [bold cyan]",
    no_args_is_help=True,
    rich_markup_mode="rich"
)


@app.command("run")
def run(
    prompt: list[str] = typer.Argument(
        None, help="Optional prompt / context text."
    ),
    model: str = typer.Option(_cfg.DEFAULT_MODEL, "--model", "-m"),
    no_stdin: bool = typer.Option(
        False,
        "--no-stdin",
        help="Force interactive mode even when stdin is detected.",
    ),
):
    execute_run(prompt=prompt, model=model, no_stdin=no_stdin)


app.add_typer(ps.app, name="ps", help="[magenta]Infrastructure monitoring.[/magenta]")

if __name__ == "__main__":
    app()
