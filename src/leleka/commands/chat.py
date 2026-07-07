from ..tools import config
from ..tools import llm_helpers

import typer
import ollama
from pathlib import Path
from datetime import datetime
from rich.live import Live
from rich.panel import Panel
from rich.console import Group
from rich.text import Text

app = typer.Typer()

@app.command("chat")
def chat_cmd(model: str = typer.Option(config.DEFAULT_MODEL, "--model", "-m")):
    llm_helpers.show_logo()
    model_file = config.MODELS_PATH / f"{model}.md"
    system_prompt = model_file.read_text(encoding="utf-8") if model_file.exists() else ""

    messages = [{"role": "system", "content": system_prompt}]
    while True:
        user_input = llm_helpers.console.input("[bold green]You:[/bold green] ")
        if user_input.lower() == "exit":
            break
        messages.append({"role": "user", "content": user_input})

        full_response = ""
        stream = ollama.chat(model=model, messages=messages, stream=True)

        # Genau wie in deiner Ur-Version: Live und Panel werden direkt hier instanziiert
        with Live(Panel("", title=f"Leleka ({model})"), console=llm_helpers.console) as live:
            for chunk in stream:
                content = chunk['message']['content']
                full_response += content
                live.update(Panel(full_response, title=f"Leleka ({model})"))

        messages.append({"role": "assistant", "content": full_response})

        # Speichern nach jeder Nachricht innerhalb der Schleife, damit nichts verloren geht
        config.CHATS_PATH.mkdir(parents=True, exist_ok=True)
        save_path = config.CHATS_PATH / f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        save_path.write_text("\n\n".join([f"{m['role']}: {m['content']}" for m in messages]), encoding="utf-8")
        # llm_helpers.console.print(f"[dim]Chat gespeichert: {save_path}[/dim]")