from __future__ import annotations
import typer
from pathlib import Path
from datetime import datetime
from leleka import config
from leleka.tools import ps_helpers
from leleka.core import llm  # Importiert deine core/llm.py
from rich.console import Console
# Logo-Import aus den Templates einfügen, falls gewünscht
# from .utils import get_leleka_logo

app = typer.Typer()
console = Console()

@app.command("chat")
def chat_cmd(
    model: str = typer.Option(config.DEFAULT_MODEL, "--model", "-m")
):
    """Interaktiver Chat-Modus mit automatischer Historie."""
    # 1. Logo anzeigen
    console.print(config.LELEKA_LOGO)

    console.print(f"Starting chat with model: {model}")

    # System Prompt laden falls vorhanden
    model_file = config.MODELS_PATH / f"{model}.md"
    system_prompt = model_file.read_text(encoding="utf-8") if model_file.exists() else ""

    # 2. Verlauf initialisieren (Hierdurch verschwindet der Pylance-Fehler!)
    messages: list[dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    # 3. Chat-Schleife
    while True:
        user_input = ps_helpers.console.input("[bold green]You:[/] ")
        if user_input.lower() == "exit":
            break

        if not user_input.strip():
            continue

        # Benutzereingabe an den Verlauf anhängen
        messages.append({"role": "user", "content": user_input})

        # --- AUSLAGERUNG AKTIVIEREN ---
        # Wir übergeben das Modell und die gesamte Historie an den Core
        assistant_response = llm.stream_leleka_response(model=model, messages=messages)

        # Die Antwort des Modells an den Verlauf anhängen, damit der Kontext bleibt
        if assistant_response:
            messages.append({"role": "assistant", "content": assistant_response})
        else:
            # Falls Fehler auftrat, die letzte User-Frage wieder entfernen
            messages.pop()

    # 4. Speichern nach dem Beenden
    if len(messages) > (1 if system_prompt else 0):
        config.CHATS_PATH.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = config.CHATS_PATH / f"chat_{timestamp}_{model}.md"

        chat_log = []
        for m in messages:
            if m["role"] != "system":
                chat_log.append(f"**{m['role'].upper()}**: {m['content']}")

        save_path.write_text("\n\n".join(chat_log), encoding="utf-8")
        ps_helpers.console.print(f"[dim]Chat gespeichert unter: {save_path}[/dim]")