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

from datetime import datetime

import typer

from leleka.config import _cfg, LELEKA_LOGO
from leleka.tools import ps_helpers, session_ops


console = ps_helpers.console


def execute_run(
    prompt: list[str] | None = None,
    model: str = _cfg.DEFAULT_MODEL,
    no_stdin: bool = False,
) -> None:
    """Callback registered on the parent Typer app via ``app.command(callback=...)``.

    Detects piped stdin for one-shot mode; otherwise enters interactive chat.

    Args:
        model: Ollama model identifier (e.g. ``"mistral:7b"``).
        no_stdin: When *True*, skip stdin detection and always enter chat mode.
    """

    ps_helpers.show_logo()

    # 1. Piped Stdin auslesen (falls vorhanden)
    piped_text = None if no_stdin else session_ops.read_stdin_if_available()

    # 2. Argumente zu einem String zusammenfügen
    cli_prompt = " ".join(prompt).strip() if prompt else None

    # 3. Stdin und Argumente kombinieren
    input_parts = []
    if piped_text:
        input_parts.append(piped_text.strip())
    if cli_prompt:
        input_parts.append(cli_prompt)

    combined_input = "\n\n".join(input_parts) if input_parts else None

    system_prompt = session_ops.load_system_prompt(model)

    # 4. Verzweigung
    if combined_input:
        _run_one_shot(model=model, system_prompt=system_prompt, input_text=combined_input)
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

    Builds a messages list (system + user), streams via ``session_ops.stream_chat``,
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

    full_response = session_ops.stream_chat(model=model, messages=messages)

    # Save one-shot session to chat history
    _cfg.CHATS_PATH.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_path = _cfg.CHATS_PATH / f"run_{timestamp}_{model}.md"
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
    Each exchange is streamed via ``session_ops.stream_chat`` and appended to *messages*.
    On exit, the full conversation (minus system messages) is saved to disk.

    Args:
        model: Ollama model identifier.
        system_prompt: Optional system prompt loaded from template.
    """

    console.print(LELEKA_LOGO)
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

        assistant_response = session_ops.stream_chat(model=model, messages=messages)

        if assistant_response:
            messages.append({"role": "assistant", "content": assistant_response})
        else:
            # Error occurred — remove the failed user message from history
            messages.pop()

    # Save chat history on exit
    _cfg.CHATS_PATH.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_path = _cfg.CHATS_PATH / f"chat_{timestamp}_{model}.md"

    chat_log: list[str] = []
    for m in messages:
        if m["role"] != "system":
            chat_log.append(f"**{m['role'].upper()}**: {m['content']}")

    save_path.write_text("\n\n".join(chat_log), encoding="utf-8")
    ps_helpers.console.print(f"[dim]Chat saved to: {save_path}[/dim]")

