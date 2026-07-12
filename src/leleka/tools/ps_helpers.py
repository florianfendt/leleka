from __future__ import annotations
import json
import os
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import TYPE_CHECKING
from leleka.config import LELEKA_LOGO

from rich.box import MINIMAL_DOUBLE_HEAD
from rich.console import Console
from rich.table import Table

if TYPE_CHECKING:
    from rich.style import Style

console = Console()


# def run_monitor() -> None:
#     """Startet nvtop für das GPU-Monitoring. Blockiert das CLI, bis nvtop beendet wird."""
#     try:
#         # Ersetzt den aktuellen Prozess durch nvtop, Terminal wird direkt übernommen
#         subprocess.run(["nvtop"], check=True)
#     except FileNotFoundError:
#         console.print("[bold red]❌ nvtop ist nicht installiert! (sudo apt install nvtop)[/bold red]")
#     except Exception as e:
#         console.print(f"[bold red]❌ Fehler beim Starten von nvtop: {e}[/bold red]")

# import subprocess
# from rich.console import Console
# from rich.table import Table
# from rich import box

def _format_size(size_bytes: int | float) -> str:
    """Konvertiert Bytes in ein lesbares Format (KB, MB, GB, TB)."""
    size = float(size_bytes)
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"

def _model_time(modified_raw: str) -> str:
    """Macht aus dem ISO-Timestamp von Ollama ein sauberes Datum."""
    if not modified_raw or modified_raw == "?":
        return "?"

    # Text-Fallback fängt Strings wie "3 weeks ago" ab
    if "T" not in modified_raw:
        return modified_raw

    try:
        # Ollama liefert oft Format wie "2024-02-14T10:15:30.1234564Z"
        # datetime.fromisoformat kommt besser mit +00:00 als mit Z klar
        clean_time = modified_raw.split(".")[0] # Millisekunden abschneiden für sauberes Parsing
        dt = datetime.fromisoformat(clean_time)
        return dt.strftime("%d.%m.%Y %H:%M")
    except ValueError:
        return modified_raw.split("T")[0] # Fallback: Nur das Datum anzeigen

# ==========================================
# DEINE URSPRÜNGLICHE FUNKTION (mit leicht optimiertem Fallback)
# ==========================================

def show_models() -> None:
    """Query the local Ollama instance and display all models in a table.

    Uses ``ollama list --json`` for structured output; falls back to the
    text-based CLI when JSON is unavailable (Ollama < 0.1.26).
    """
    # --- try JSON first, fall back to text parsing -------------------------
    models: list[dict[str, object]] | None = None

    for args in [["ollama", "list", "--json"], ["ollama", "list"]]:
        try:
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                check=True,
                timeout=10,
            )
        except FileNotFoundError:
            console.print(
                "[bold red]❌ Das 'ollama' CLI-Tool wurde nicht gefunden. "
                "Ist Ollama installiert?[/bold red]"
            )
            return
        except subprocess.TimeoutExpired:
            console.print(
                "[bold red]❌ Timeout beim Abfragen von Ollama (10s). "
                "Läuft Ollama noch?[/bold red]"
            )
            return
        except subprocess.CalledProcessError as e:
            stderr = e.stderr or "(leer)"
            console.print(
                f"[bold red]❌ Fehler bei der Abfrage von Ollama: {stderr}[/bold red]"
            )
            return

        # Attempt JSON parse first
        try:
            models = json.loads(result.stdout)
            # Manche Ollama-Versionen packen die Modelle in einen Key "models"
            if isinstance(models, dict) and "models" in models:
                models = models["models"]
                break
            elif isinstance(models, list):
                break  # success
        except (json.JSONDecodeError, TypeError):
            pass

        # Fallback: text-based parsing
        lines = result.stdout.strip().split('\n')
        if len(lines) < 2:
            console.print(
                "[bold yellow]⚠️ Keine Ollama-Modelle gefunden "
                "oder Ollama läuft nicht.[/bold yellow]"
            )
            return

        headers = lines[0].split()
        models = []
        for line in lines[1:]:
            parts = line.split(maxsplit=len(headers) - 1)
            if len(parts) == len(headers):
                models.append(dict(zip(headers, parts)))

    # --- render table -------------------------------------------------------
    if not models:
        console.print(
            "[bold yellow]⚠️ Keine Ollama-Modelle gefunden "
            "oder Ollama läuft nicht.[/bold yellow]"
        )
        return

    table = Table(
        title="🧠 LOCAL OLLAMA MODELS",
        box=MINIMAL_DOUBLE_HEAD,
        title_style="bold magenta",
    )
    table.add_column("Name", style="cyan", justify="left")
    table.add_column("ID", style="dim", justify="left")
    table.add_column("Größe", style="yellow", justify="right")
    table.add_column("Modifiziert", style="green", justify="left")

    for model in models:
        # JSON path (primary) oder Fallback (Keys sind dann oft großgeschrieben wie "NAME")
        name = model.get("name") or model.get("NAME", "?")

        # ID ist manchmal "model_id" oder "ID" oder "digest"
        model_id = str(model.get("model_id") or model.get("digest") or model.get("ID", "?"))[:12]

        size_bytes = model.get("size")
        if isinstance(size_bytes, (int, float)):
            size_human = _format_size(size_bytes)
        else:
            # Falls wir im Text-Fallback gelandet sind, steht die Größe schon als String drin (z.B. "4.7 GB")
            size_human = str(model.get("SIZE", "?"))

        modified_raw = model.get("modified_at") or model.get("MODIFIED", "")
        modified_str = _model_time(str(modified_raw))

        table.add_row(str(name), model_id, size_human, modified_str)

    console.print(table)


def show_system_pulse():
    """Liest die System-Matrix aus und rendert sie."""

    # Hol dir den Pfad direkt aus der .bashrc
    # WICHTIG: Ersetze "DEIN_VARIABLEN_NAME" mit dem exakten Namen aus deiner .bashrc!
    raw_path = os.getenv("$PULSE")

    if not raw_path:
        console.print("[bold red]❌ Umgebungsvariable für den Puls ist im System nicht gesetzt![/bold red]")
        return

    # expanduser() wandelt eine eventuelle Tilde (~) in den echten Home-Pfad um
    pulse_file = Path(raw_path).expanduser()

    if not pulse_file.exists():
        console.print(f"[bold red]❌ Puls-Datei nicht gefunden unter: {pulse_file}[/bold red]")
        return

    try:
        # Datei laden
        with open(pulse_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Ab hier kommt dein Code für die rich-Matrix
        console.print(f"[bold green]System Puls ({pulse_file.name}) erfolgreich geladen![/bold green]")
        # ...

    except Exception as e:
        console.print(f"[bold red]❌ Fehler beim Lesen des Pulses: {e}[/bold red]")

def show_logo() -> str:
    """Lädt das Logo dynamisch aus dem globalen Templates-Ordner."""
    try:
        # __file__ ist src/leleka/commands/chat.py
        # .parents[3] geht hoch zu: 1. commands -> 2. leleka -> 3. src -> 4. Root (Top Level)
        project_root = Path(__file__).resolve().parents[3]
        logo_path = LELEKA_LOGO

        if logo_path.exists():
            # Datei einlesen
            content = logo_path.read_text(encoding="utf-8")

            # Da in deiner Datei noch 'LELEKA_LOGO = r"""' und '"""' steht,
            # filtern wir nur die Zeilen heraus, die das eigentliche ASCII/Rich-Logo enthalten.
            logo_lines = []
            for line in content.splitlines():
                # Überspringe die Python-Zuweisung, die Markdown-Überschrift und die Anführungszeichen
                if line.strip().startswith(("#", "LELEKA_LOGO", '"""', '""')):
                    continue
                logo_lines.append(line)

            return "\n".join(logo_lines)
    except Exception:
        pass

    # Fallback, falls die Datei mal nicht gefunden wird
    return "[bold magenta]>> Leleka CLI <<[/bold magenta]"