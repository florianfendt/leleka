import typer
from rich.console import Console
from leleka.tools.ps_helpers import show_system_pulse, show_models

app = typer.Typer(help="System-Infrastruktur steuern")
console = Console()

@app.callback(invoke_without_command=True)
def ps_main(
    pulse: bool = typer.Option(False, "--pulse", help="Table of projects registered to system"),
    models: bool = typer.Option(False, "--models", help="Status about installed and running Ollama models."),
) -> None:
    if pulse:
        show_system_pulse()
    elif models:
        console.print("[bold magenta]🧠 Ollama Models Overview...[/bold magenta]")
        show_models()
    else:
        console.print("[yellow]Action 'ps' needs --pulse or --models.[/yellow]")