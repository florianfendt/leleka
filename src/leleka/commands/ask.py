from leleka.config import MODELS_PATH
from leleka.tools import ps_helpers
import os
import typer
import ollama
from pathlib import Path
from rich.live import Live
from rich.panel import Panel


app = typer.Typer()

@app.command("ask")
def ask_cmd(
    prompt: str = typer.Argument(..., help="Prompt"),
    model: str = typer.Option("gemma4:12b", "--model", "-m"),
    file: Path = typer.Option(None, "--file", "-f")
):
    ps_helpers.show_logo()

    model_file = MODELS_PATH / f"{model}.md"
    system_prompt = model_file.read_text(encoding="utf-8") if model_file.exists() else ""
    context = file.read_text(encoding="utf-8") + "\n" if file and file.exists() else ""

    response_stream = ollama.generate(model=model, prompt=context + prompt, system=system_prompt, stream=True)
    answer = ""
    # Hier rufen wir unsere neue UI-Funktion auf:
    with ps_helpers.create_streaming_panel("", title=f"Leleka ({model})", title_color="magenta", border_color="cyan") as live:
        for chunk in response_stream:
            answer += chunk.get('response', '')

            # Zum Aktualisieren übergeben wir ein neues Panel mit den gleichen Styles
            live.update(Panel(answer, title=f"[magenta]Leleka ({model})[/magenta]", border_style="cyan"))

            if chunk.get('done'):
                stats = ps_helpers.calc_token_stats(chunk)
                ps_helpers.show_context_stats(stats)