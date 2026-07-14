"""Shared test fixtures for leleka tests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture()
def tmp_project_dir(tmp_path: Path) -> Path:
    """Provide a temporary directory pre-populated with minimal project structure.

    Creates::

        tmp_project_dir/
        ├── paths.json          (minimal valid structure)
        └── templates/
            └── default.md      (sample template)

    Returns the *tmp_project_dir* path so callers can add more files on top.
    """
    # Write a minimal paths.json that PathEngine expects
    paths_data = {
        "paths": {"CONTEXT": str(tmp_path / "context"), "MODELS": str(tmp_path / "models")},
        "targets": {},
    }
    (tmp_path / "paths.json").write_text(json.dumps(paths_data), encoding="utf-8")

    # Write a sample template
    template = tmp_path / "templates" / "default.md"
    template.parent.mkdir(parents=True, exist_ok=True)
    template.write_text("# Title\n\n## Abstract\n\n## Status\n", encoding="utf-8")

    return tmp_path


@pytest.fixture()
def sample_messages() -> list[dict[str, str]]:
    """Return a minimal conversation history in Ollama chat format."""
    return [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"},
    ]


@pytest.fixture()
def sample_done_chunk() -> dict[str, object]:
    """Return a realistic Ollama ``done`` chunk for testing token stats."""
    return {
        "model": "mistral:7b",
        "created_at": "2024-06-15T10:30:00Z",
        "done": True,
        "total_duration": 1_200_000_000,
        "load_duration": 50_000_000,
        "prompt_eval_count": 256,
        "prompt_eval_duration": 80_000_000,
        "eval_count": 128,
        "eval_duration": 900_000_000,
    }


@pytest.fixture()
def minimal_template(tmp_path: Path) -> Path:
    """Return a path to a simple Markdown template file."""
    tpl = tmp_path / "template.md"
    tpl.write_text("# Title\n\n## Abstract\n\n## Methodology\n", encoding="utf-8")
    return tpl
