"""Streaming engine — delegates to ``session_ops.stream_chat()``."""

from __future__ import annotations


def stream_leleka_response(model: str, messages: list[dict[str, str]]) -> str:
    """Stream an Ollama chat response with a live Rich panel.

    Returns the full concatenated text or ``""`` on error.
    """
    from leleka.tools import session_ops
    return session_ops.stream_chat(model=model, messages=messages)
