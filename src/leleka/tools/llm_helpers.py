from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from . import config

console = Console()

def calc_token_stats(leleka_res: dict) -> dict:
    """Berechnet Token-Metriken aus der Ollama-Response."""
    return {
        "context": leleka_res.get("prompt_eval_count", 0),
        "response": leleka_res.get("eval_count", 0),
        "context_size": 8192  # Fester Wert als Fallback
    }

def show_context_stats(stats: dict):
    """Gibt die Stats direkt im Terminal aus."""
    usage = (stats["context"] + stats["response"]) / stats["context_size"]
    console.print(f"[dim]Input: {stats['context']} | Response: {stats['response']} | Usage: {usage:.2%}[/dim]")

def show_logo():
    """Gibt das Leleka-Logo formatiert im Terminal aus."""
    console.print(config.LELEKA_LOGO)