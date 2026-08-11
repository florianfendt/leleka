"""Shared session helpers for the unified ``run`` command.

Handles system-prompt loading, streaming panel rendering, token-stats display,
and chat persistence.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import ollama
from rich.live import Live
from rich.panel import Panel

from leleka.config import _cfg
from leleka.tools._ui import console


@dataclass(frozen=True)
class TokenStats:
    """Immutable token-usage snapshot from an Ollama chunk."""
    context: int
    response: int
    context_size: int = 8192


def load_system_prompt(model: str) -> str | None:
    """Load the system prompt for *model* from ``MODELS_PATH``.

    Returns ``None`` when no matching model file exists.
    """
    model_file = _cfg.MODELS_PATH / f"{model}.md"
    if model_file.exists():
        return model_file.read_text(encoding="utf-8")
    return None


def render_stream(
    *,
    title: str,
    border_style: str = "cyan",
) -> Iterator[tuple[Live, Panel]]:
    """Context-manager that yields a Rich ``Live`` + ``Panel`` for streaming.

    Usage::

        with render_stream(title="Leleka (mistral:7b)") as (live, panel):
            live.update(Panel(full_text, title=title, border_style=border_style))
    """
    with Live(
        Panel("", title=title, border_style=border_style),
        console=console,
    ) as live:
        yield live, live.console


def stream_chat(model: str, messages: list[dict[str, str]]) -> str:
    """Stream an Ollama chat response with a live Rich panel.

    Returns the full concatenated text or ``""`` on error.
    """
    console.print(f"[bold cyan]Starte Generierung mit {model}...[/bold cyan]\n")

    try:
        response_stream = ollama.chat(
            model=model,
            messages=messages,
            stream=True,
        )
    except Exception as e:
        console.print(f"[bold red]❌ Error connecting to Ollama: {e}[/bold red]")
        return ""

    full_response = ""
    token_stats = TokenStats(context=0, response=0)
    raw_ts = "unknown_time"

    with Live(Panel("", title=f"Leka ({model})", border_style="cyan"), console=console) as live:
        for chunk in response_stream:
            message_chunk = chunk.get("message", {})
            content = message_chunk.get("content", "")
            full_response += content
            live.update(Panel(full_response, title=f"Leka ({model})", border_style="cyan"))

            if chunk.get("done"):
                raw_ts = chunk.get("created_at", raw_ts)
                token_stats = _chunk_to_token_stats(chunk)

    show_token_stats(token_stats)
    return full_response


def _chunk_to_token_stats(chunk: dict[str, object]) -> TokenStats:
    """Convert an Ollama ``done`` chunk into a ``TokenStats`` dataclass.

    Extracts *prompt_eval_count*, *eval_count*, and *context_size* from the
    raw Ollama payload, defaulting to 0 / 8192 when absent.
    """
    context = int(chunk.get("prompt_eval_count", 0))
    response = int(chunk.get("eval_count", 0))
    ctx_size = int(chunk.get("context_size", 8192))
    return TokenStats(context=context, response=response, context_size=ctx_size)


def show_token_stats(stats: TokenStats) -> None:
    """Display token-usage stats in a compact format."""
    console.print(
        f"[dim]Token Stats — Context: {stats.context:,} / "
        f"Response: {stats.response:,} / "
        f"Context Size: {stats.context_size:,}[/dim]"
    )


def save_chat(messages: list[dict[str, str]], model: str) -> Path:
    """Save chat messages as markdown to ``CHATS_PATH``.

    Returns the path of the saved file.
    """
    from datetime import datetime

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_model = model.replace("/", "_").replace(":", "_")
    filename = f"chat_{ts}_{safe_model}.md"
    chat_dir = _cfg.CHATS_PATH
    chat_dir.mkdir(parents=True, exist_ok=True)
    filepath = chat_dir / filename

    lines: list[str] = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        label = "User" if role == "user" else "Leka"
        lines.append(f"### {label}\n\n{content}\n\n---\n\n")

    filepath.write_text("\n".join(lines), encoding="utf-8")
    console.print(f"[dim]Chat saved to {filepath}[/dim]")
    return filepath


def read_stdin_if_available() -> str | None:
    """Read all of stdin when it is **not** a TTY (piped input).

    Returns the piped text, or ``None`` when nothing was piped.
    """
    if not sys.stdin.isatty():
        return sys.stdin.read()
    return None
