import typer
from rich.console import Console
from commands.ai_commands import app as ai_app
from commands.system_commands import app as sys_app

app = typer.Typer(
    name="Leleka",
    help="[bold cyan] LELEKA CLI AI [bold cyan]",
    no_args_is_help=True,
    rich_markup_mode="rich"
)
console = Console()

# Direktes Einhängen der Kommandos auf der obersten Ebene
# Dadurch bleiben deine gewohnten CLI-Befehle exakt gleich!
app.add_typer(ai_app, help="[cyan]AI Commands[/cyan]")
app.add_typer(sys_app, help="[magenta]System-Commands[/magenta]")
app.add_typer(build_app, help="[yellow]Build & Train Commands[/yellow]")
if __name__ == "__main__":
    app()