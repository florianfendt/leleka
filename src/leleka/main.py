import typer
from rich.console import Console
from leleka.commands import ask, chat, ps
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
):
    """Run Leleka — interactive chat or one-shot prompt from piped text."""
    execute_run(model=model, no_stdin=no_stdin)


@app.command("ask")
def _deprecated_ask(
    prompt: str = typer.Argument(..., help="Prompt"),
):
    console.print("[yellow][DEPRECATED][/yellow] 'ask' is deprecated. Use '[bold]leleka run[/bold]' instead.")
    raise typer.Exit()


@app.command("chat")
def _deprecated_chat():
    console.print("[yellow][DEPRECATED][/yellow] 'chat' is deprecated. Use '[bold]leleka run[/bold]' instead.")
    raise typer.Exit()

app.add_typer(ps.app, name="ps", help="[magenta]Infrastructure monitoring.[/magenta]")

if __name__ == "__main__":
    app()
