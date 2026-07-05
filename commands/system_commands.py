"""
ARCHITECTURAL PURPOSE:
Provides system infrastructure control orchestration commands. It manages deployment
activities by executing Wake-on-LAN (WoL) system initialization broadcasts and initializing
secure shell (SSH) connection wrappers or localized script pipelines to stand up network assets.

ROADMAP & OPTIMIZATIONS:
1. Shift low-level shell execution targets to Python-native networking implementations for higher portability.
2. Integrate connection checks to ensure target machines are responsive before firing downline terminal sessions.
3. Unify placeholder structures into a modular subcommand configuration structure.
"""

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
    Architectural Purpose:
    Sends Magic Packet sequences to wake specific host infrastructure and opens terminal operational sessions.

    Input Parameters:
    - device (str): Key matching configured hardware profiles.
    - env (bool): Flags whether localized initialization scripts run alongside basic routing.

    Return Values:
    - None

    Side Effects / Algorithmic Logic:
    Fires out independent external subprocess tracking chains (`wakeonlan`, `kitty`), writes to standard output, and exits via system errors if invalid device declarations hit verification blocks.
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