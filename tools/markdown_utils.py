"""
file_name: markdown_utils.py
description: Pure functions for Markdown parsing, heading shifting, and code block wrapping.
"""

import re

def shift_headings(content: str) -> str:
    """
    Erhöht die Heading-Ebene um eins, schützt aber Metadaten-Blöcke (> [!META]).
    Verhindert, dass die Dokumentenstruktur innerhalb des Gesamtkontexts bricht.
    """
    return re.sub(r'^(?![ \t]*>)(#+ )', r'#\1', content, flags=re.MULTILINE)

def wrap_in_code_block(content: str, language: str) -> str:
    """
    Verpackt rohen Text sauber in einen Markdown-Codeblock für das LLM.
    """
    return f"```{language}\n{content.strip()}\n```\n"
