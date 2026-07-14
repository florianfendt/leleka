"""Unified ``run`` command — merges ``ask`` and ``chat`` into one entry point.

CLI shape::

    leleka run                          # interactive chat (default)
    leleka run --model mistral:7b       # interactive with model selection
    cat file.txt | leleka run           # pipe text → one-shot mode
    leleka run --no-stdin               # force interactive even when stdin detected

When **stdin is piped** the content becomes raw input fed directly to the LLM.
No distinction between "context" and "prompt" — it's all just text going in.
"""

from __future__ import annotations

import sys
from pathlib import Path
from datetime import datetime

import typer
import ollama
from rich.console import Console
from rich.live import Live
from rich.panel import Panel

from leleka import config
from leleka.tools import ps_helpers, session_ops


console = Console()


def execute_run(
    model: str = config.DEFAULT_MODEL,
    no_stdin: bool = False,
) -> None:
    """Callback registered on the parent Typer app via ``app.command(callback=...)``.

    Detects piped stdin for one-shot mode; otherwise enters interactive chat.

    Args:
        model: Ollama model identifier (e.g. ``"mistral:7b"``).
        no_stdin: When *True*, skip stdin detection and always enter chat mode.
    """

    ps_helpers.show_logo()

    # ------------------------------------------------------------------
    # 1. Detect whether we have piped input (one-shot) or not (interactive)
    # ------------------------------------------------------------------
    piped_text = None if no_stdin else session_ops.read_stdin_if_available()

    system_prompt = session_ops.load_system_prompt(model)

    if piped_text is not None:
        _run_one_shot(model=model, system_prompt=system_prompt, input_text=piped_text)
    else:
        _run_chat(model=model, system_prompt=system_prompt)


# ------------------------------------------------------------------
# One-shot mode (like the old ``ask`` command)
# ------------------------------------------------------------------

def _run_one_shot(
    model: str,
    system_prompt: str | None,
    input_text: str,
) -> None:
    """Feed *input_text* to the LLM in one shot and stream the response.

    Builds a messages list (system + user), streams via ``_stream_chat``,
    then saves the exchange to chat history.

    Args:
        model: Ollama model identifier.
        system_prompt: Optional system prompt loaded from template.
        input_text: Raw text received on stdin.
    """

    prompt = input_text.strip()
    if not prompt:
        console.print("[yellow]No text received on stdin — nothing to send.[/yellow]")
        return

    # Build messages list (ollama.chat style)
    messages: list[dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    full_response = _stream_chat(model=model, messages=messages)

    # Save one-shot session to chat history
    config.CHATS_PATH.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_path = config.CHATS_PATH / f"run_{timestamp}_{model}.md"
    save_path.write_text(
        f"**USER**: {prompt}\n\n**ASSISTANT**: {full_response}",
        encoding="utf-8",
    )


# ------------------------------------------------------------------
# Interactive chat mode (like the old ``chat`` command)
# ------------------------------------------------------------------

def _run_chat(model: str, system_prompt: str | None) -> None:
    """Interactive REPL loop with automatic history saving.

    Prompts the user for input in a ``while True`` loop; exits on ``exit``.
    Each exchange is streamed via ``_stream_chat`` and appended to *messages*.
    On exit, the full conversation (minus system messages) is saved to disk.

    Args:
        model: Ollama model identifier.
        system_prompt: Optional system prompt loaded from template.
    """

    console.print(config.LELEKA_LOGO)
    console.print(f"[dim]Starting chat with model: {model}[/dim]")

    messages: list[dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    while True:
        user_input = ps_helpers.console.input("[bold green]You:[/] ")
        if user_input.lower() == "exit":
            break
        if not user_input.strip():
            continue

        messages.append({"role": "user", "content": user_input})

        assistant_response = _stream_chat(model=model, messages=messages)

        if assistant_response:
            messages.append({"role": "assistant", "content": assistant_response})
        else:
            # Error occurred — remove the failed user message from history
            messages.pop()

    # Save chat history on exit
    config.CHATS_PATH.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_path = config.CHATS_PATH / f"chat_{timestamp}_{model}.md"

    chat_log: list[str] = []
    for m in messages:
        if m["role"] != "system":
            chat_log.append(f"**{m['role'].upper()}**: {m['content']}")

    save_path.write_text("\n\n".join(chat_log), encoding="utf-8")
    ps_helpers.console.print(f"[dim]Chat saved to: {save_path}[/dim]")


# ------------------------------------------------------------------
# Shared streaming helper (used by both modes)
# ------------------------------------------------------------------

def _stream_chat(model: str, messages: list[dict[str, str]]) -> str:
    """Stream an Ollama chat response and return the full text.

    Renders a live Rich Panel while tokens arrive.  Returns ``""`` on error.

    Args:
        model: Ollama model identifier.
        messages: Conversation history in Ollama chat format.

    Returns:
        Concatenated response text, or empty string on connection failure.
    """
    console.print(f"[bold cyan]Starte Generierung mit {model}...[/bold cyan]\n")

    try:
        response_stream = ollama.chat(
            model=model,
            messages=messages,
            stream=True,
        )
    except Exception as e:
        ps_helpers.console.print(f"[bold red]❌ Error connecting to Ollama: {e}[/bold red]")
        return ""

    full_response = ""
    token_stats = {"context": 0, "response": 0, "context_size": 8192}

    with Live(
        Panel("", title=f"Leka ({model})", border_style="cyan"),
        console=ps_helpers.console,
    ) as live:
        for chunk in response_stream:
            message_chunk = chunk.get("message", {})
            content = message_chunk.get("content", "")
            full_response += content

            live.update(Panel(full_response, title=f"Leka ({model})", border_style="cyan"))

            if chunk.get("done"):
                token_stats["context"] = chunk.get("prompt_eval_count", 0)
                token_stats["response"] = chunk.get("eval_count", 0)

    session_ops.show_token_stats_from_chunk(token_stats)
    return full_response
