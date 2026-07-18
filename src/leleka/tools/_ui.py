"""Shared UI primitives for the Leleka CLI.

Provides a single ``Console`` singleton so all tool modules render to the same
terminal without creating duplicate Rich console instances.
"""

from __future__ import annotations

from rich.console import Console

console = Console()
