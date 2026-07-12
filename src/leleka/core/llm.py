from __future__ import annotations
import ollama
from rich.live import Live
from rich.panel import Panel
from leleka.tools import ps_helpers  # Für die Konsole

def stream_leleka_response(model: str, messages: list[dict[str, str]]) -> str:
    """Spawns interactive network generation loops tracking streaming Ollama chat payloads.

    Renders the live response in a Rich Panel and returns the final string.
    """
    ps_helpers.console.print(f"[bold cyan]Starte Generierung mit {model}...[/bold cyan]\n")

    try:
        # Wir nutzen .chat() für echten Gesprächsverlauf, stream=True für das Live-Erlebnis
        response_stream = ollama.chat(
            model=model,
            messages=messages,
            stream=True
        )
    except Exception as e:
        ps_helpers.console.print(f"[bold red]❌ Error connecting to Ollama: {e}[/bold red]")
        return ""

    full_response = ""
    token_stats = {"context": 0, "response": 0, "context_size": 8129}
    raw_ts = "unknown_time"

    # Live-Panel starten
    with Live(Panel("", title=f"Leka ({model})", border_style="cyan"), console=ps_helpers.console) as live:
        for chunk in response_stream:
            # Bei ollama.chat() liegt der Text in chunk['message']['content']
            message_chunk = chunk.get('message', {})
            content = message_chunk.get('content', '')
            full_response += content

            # Panel aktualisieren
            live.update(Panel(full_response, title=f"Leka ({model})", border_style="cyan"))

            # Statistiken sichern, falls vorhanden
            if chunk.get('done'):
                # Hier kannst du deine calc_token_stats(chunk) aufrufen falls definiert
                raw_ts = chunk.get('created_at', raw_ts)

    # Statistiken am Ende anzeigen
    # show_context_stats(token_stats)

    return full_response