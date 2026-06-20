import typer
import subprocess
from core.config import MAC_ADDRESSES

app = typer.Typer()

@app.command("switanok")
def switanok(
    device: str = typer.Argument("bradley", help="Ziel-Device (bradley, ferrari, falcon)"),
    env: bool = typer.Option(True, "-e/-E", help="Entwicklungsumgebung direkt mit starten")
) -> None:
    """
    [bold magenta]Infrastruktur-Command Switanok:[/bold magenta] Weckt Systeme via WoL und baut SSH-Tunnel.
    """
    # Überprüfen, ob das Gerät in der config.json existiert
    if device not in MAC_ADDRESSES:
        typer.echo(f"Fehler: Keine MAC-Adresse für '{device}' in der config.json gefunden.")
        raise typer.Exit(code=1)

    target = MAC_ADDRESSES[device]
    subprocess.run(["wakeonlan", target], capture_output=True)

    if env and device == "bradley":
        subprocess.Popen(["./02_tools/hosts/dev_hosts/launch_coding_env.sh"])
    else:
        subprocess.run(["kitty", "ssh", f"flo@{device}"])
        typer.echo(f"SSH-Verbindung zu {device} initialisiert.")

# --- PLATZHALTER FÜR DEINE WEITEREN REFACTORINGS ---
# @app.command("broom")
# def broom():
#     """Hier klinken wir als Nächstes den WorkspaceBroom ein!"""
#     pass