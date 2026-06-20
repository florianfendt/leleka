import typer
import subprocess
from pathlib import Path
from rich.console import Console

# 1. Wir holen den zuverlässigen Pfad direkt aus deiner Config
from core.config import WORKSPACE_ROOT

# 2. Wir importieren die Rezepte und die Hilfsfunktion aus dem Core
from core.context import get_recipes

# 3. Wir nutzen deinen fertigen Scraper aus den Tools
from tools.workspace_ops import scrape_context_from_files

app = typer.Typer(help="Compiler & Trainings-Befehle für leleka_v0.1")
console = Console()

# ==========================================
# COMMAND 1: CONTEXT SCRAPER (BUILD)
# ==========================================
@app.command("build-context")
def build_context(
    profile: str = typer.Argument(..., help="Profil ('user', 'pro', 'all') zum Scrapen")
):
    """
    Sammelt die definierten Markdown/CSV-Dateien und baut die systemformed.txt
    """
    recipes = get_recipes(profile)

    for recipe in recipes:
        console.print(f"\n[bold cyan]🔨 Baue Kontext für '{recipe['model_name']}'...[/bold cyan]")

        target_dir = WORKSPACE_ROOT / recipe["target_dir"]
        target_dir.mkdir(parents=True, exist_ok=True)
        target_file = target_dir / "systemformed.txt"

        # Pfade in absolute Path-Objekte umwandeln für deinen Scraper
        source_paths = [WORKSPACE_ROOT / src for src in recipe["sources"]]

        # Deinen bestehenden Scraper aufrufen!
        final_context = scrape_context_from_files(source_paths)

        if not final_context.strip():
            console.print(f"[bold red]  ❌ Fehler: Konnte keinen Kontext generieren (Dateien leer/fehlend).[/bold red]")
            continue

        target_file.write_text(final_context, encoding='utf-8')
        console.print(f"[bold green]  ✅ systemformed.txt erfolgreich in {target_dir.name} generiert![/bold green]")


# ==========================================
# COMMAND 2: MODEL TRAINER
# ==========================================
@app.command("train")
def train_model(
    profile: str = typer.Argument(..., help="Profil ('user', 'pro', 'all') zum Trainieren")
):
    """
    Prüft die Bedingungen und trainiert das Ollama-Modell neu.
    """
    recipes = get_recipes(profile)

    for recipe in recipes:
        console.print(f"\n[bold magenta]🚀 Prüfe Trainings-Bedingungen für '{recipe['model_name']}'...[/bold magenta]")

        target_dir = WORKSPACE_ROOT / recipe["target_dir"]
        modelfile_path = target_dir / "Modelfile"
        systemformed_path = target_dir / "systemformed.txt"

        # Bedingungs-Prüfung
        if not target_dir.exists():
            console.print(f"[bold red]  ❌ Ordner {target_dir.name} existiert nicht![/bold red]")
            continue
        if not modelfile_path.exists():
            console.print(f"[bold red]  ❌ Kein 'Modelfile' im Ordner gefunden![/bold red]")
            continue
        if not systemformed_path.exists():
            console.print(f"[bold red]  ❌ Keine 'systemformed.txt' gefunden! (Bitte vorher 'build-context' ausführen)[/bold red]")
            continue

        # Alles erfüllt -> Go!
        console.print(f"[bold green]  🧠 Starte Ollama Training für {recipe['model_name']}...[/bold green]")
        try:
            result = subprocess.run(
                ["ollama", "create", recipe["model_name"], "-f", "Modelfile"],
                cwd=target_dir,
                capture_output=True,
                text=True,
                check=True
            )
            console.print(f"[bold green]  🎉 ERFOLG! Modell '{recipe['model_name']}' ist einsatzbereit.[/bold green]")
        except subprocess.CalledProcessError as e:
            console.print(f"[bold red]  ❌ OLLAMA FEHLER beim Build:[/bold red]")
            console.print(f"[red]{e.stderr}[/red]")
        except FileNotFoundError:
            console.print("[bold red]  ❌ OLLAMA CLI nicht gefunden. Ist Ollama installiert?[/bold red]")