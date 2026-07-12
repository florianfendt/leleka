import typer
from rich.console import Console
from leleka.commands import ask, chat,ps

app = typer.Typer(
    name="Leleka",
    help="[bold cyan] LELEKA CLI AI [bold cyan]",
    no_args_is_help=True,
    rich_markup_mode="rich"
)
console = Console()

# Direktes Einhängen der Kommandos auf der obersten Ebene
# Dadurch bleiben deine gewohnten CLI-Befehle exakt gleich!
app.add_typer(ask.app, help="[cyan]AI Commands[/cyan]")
app.add_typer(chat.app, help="[magenta]System-Commands[/magenta]")
app.add_typer(ps.app, name="ps", help="[magenta]Infrastructure monitoring.[/magenta]")

if __name__ == "__main__":
    app()