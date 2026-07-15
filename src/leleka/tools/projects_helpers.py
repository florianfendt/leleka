"""Business logic for project scaffolding.

All functions take explicit parameters and return results.
No CLI I/O (no print, no typer.Exit) — fully testable with mock paths.
"""
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from leleka.core.projects_engine import ProjectFile


console = Console()

def initialize_project_doc(target_md: Path, template_md: Path, initial_data: dict[str, str]) -> ProjectFile:
    """Initialisiert ein strukturiertes Markdown-Projektfile basierend auf einem Template.

    Befüllt die erlaubten Kapitel mit initialen Werten (z.B. Name, Typ, Abstract).
    """
    # Instanziieren (liest bestehende Datei ein oder startet leer)
    doc = ProjectFile(filepath=target_md, template_path=template_md)

    # Befüllen der Kapitel anhand der übergebenen Daten
    for header, content in initial_data.items():
        # Sicherstellen, dass wir die H2-Syntax einhalten
        formatted_header = header if header.startswith("## ") else f"## {header}"
        doc.update_chapter(formatted_header, content)

    # Die save() Methode sorgt dafür, dass die Template-Struktur erzwungen wird
    doc.save()
    return doc


def update_project_chapter(target_md: Path, template_md: Path, header: str, new_content: str) -> None:
    """Updates or initiates a chapter within the project_file"""
    doc = ProjectFile(filepath=target_md, template_path=template_md)

    formatted_header = header if header.startswith("## ") else f"## {header}"
    doc.update_chapter(formatted_header, new_content)

    doc.save()


def log_sys_pulse(project_id: str, project_type: str, abstract: str) -> dict[str, Any]:
    """Log a system pulse event for the given project.

    Returns the payload that was logged (useful for testing).
    """
    payload = {
        "project_id": project_id,
        "project_type": project_type,
        "abstract": abstract,
    }
    # Return of payload
    return payload



def calc_token_stats(leleka_res: dict[str, object]) -> dict[str, int]:
    """Calculate token usage statistics from an Ollama response chunk.

    Args:
        leleka_res: Raw ``done`` chunk from the Ollama streaming API.

    Returns:
        Dict with keys *context*, *response*, and *context_size* (int).
    """
    return {
        "context": int(leleka_res.get("prompt_eval_count", 0)),
        "response": int(leleka_res.get("eval_count", 0)),
        "context_size": 8192,  # Fixed fallback value
    }


def show_context_stats(stats: dict[str, int]) -> None:
    """Display token-usage statistics to the console.

    Args:
        stats: Dict with *context*, *response*, and *context_size* keys.
    """
    usage = (stats["context"] + stats["response"]) / stats["context_size"]
    console.print(f"[dim]Input: {stats['context']} | Response: {stats['response']} | Usage: {usage:.2%}[/dim]")

