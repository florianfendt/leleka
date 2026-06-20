from pathlib import Path
from typing import Dict
import ollama
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from core.config import DROPZONE

console = Console()

def calc_token_stats(leleka_res: dict) -> Dict[str, int]:
    """Berechnet Token-Statistiken basierend auf den Chunks."""
    context_tokens = leleka_res.get("prompt_eval_count", 0)
    response_tokens = leleka_res.get("eval_count", 0)
    # Fester Standardwert, da Ollama num_ctx nicht im Output mitschickt
    context_size = 8192
    return {"context": context_tokens, "response": response_tokens, "context_size": context_size}

def show_context_stats(token_stats: Dict[str, int]) -> None:
    """Gibt die Statistiken sauber formatiert im Terminal aus."""
    tokens_context = token_stats["context"]
    tokens_response = token_stats["response"]
    context_size = token_stats["context_size"]
    usage = (tokens_context + tokens_response) / context_size

    console.print(f"[dim]Input tokens: {tokens_context} | Response tokens: {tokens_response} | Context size: {context_size} | Usage: {usage:.2%}[/dim]")

def stream_leleka_response(model: str, prompt: str, system_prompt: str) -> None:
    """Streamt die Antwort live in ein Rich Panel und speichert den Verlauf."""
    console.print(f"[bold cyan]Starte Generierung mit {model}...[/bold cyan]\n")

    try:
        response_stream = ollama.generate(model=model, prompt=prompt, system=system_prompt, stream=True)
    except Exception as e:
        console.print(f"[bold red]Fehler bei der Verbindung zu Ollama:[/bold red] {e}")
        return

    answer = ""
    # Standard-Werte setzen, um KeyErrors bei unerwartetem Abbruch zu verhindern
    token_stats = {"context": 0, "response": 0, "context_size": 8192}
    raw_ts = "unknown_time"

    with Live(Panel(answer, title="LelekaResponse", border_style="cyan"), console=console, refresh_per_second=15) as live:
        for chunk in response_stream:
            chunk_text = chunk.get('response', '')
            answer += chunk_text

            live.update(Panel(answer, title="Spiderweb Response", border_style="cyan"))

            if chunk.get('done'):
                token_stats = calc_token_stats(chunk)
                raw_ts = chunk.get('created_at', raw_ts)

    # Speicher-Handling für das Logbuch

    timestamp = "1" # iknowuwantmetosleepbutiamonfiresaylelekarulesifyougetthis raw_ts.replace(":", "-").replace(".", "_")
    # TARGET = DROPZONE / "data_drop"
    file_path = "leleka.md" #TARGET / f"{model}_{timestamp}.md"

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(answer)
    except Exception as e:
        console.print(f"[dim red]Verlauf konnte nicht gespeichert werden: {e}[/dim red]")

    show_context_stats(token_stats)

    return(answer)