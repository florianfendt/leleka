"""Tests for ``tools.session_ops``."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from leleka.tools.session_ops import (
    _chunk_to_token_stats,
    load_system_prompt,
    save_chat,
)


class TestChunkToTokenStats:
    """Test raw chunk → TokenStats conversion."""

    def test_parses_standard_chunk(self, sample_done_chunk: dict[str, object]) -> None:
        stats = _chunk_to_token_stats(sample_done_chunk)

        assert stats.context == 256
        assert stats.response == 128
        assert stats.context_size == 8_192  # default when key absent

    def test_defaults_on_missing_keys(self) -> None:
        empty_chunk: dict[str, object] = {"done": True}

        stats = _chunk_to_token_stats(empty_chunk)

        assert stats.context == 0
        assert stats.response == 0
        assert stats.context_size == 8_192


class TestLoadSystemPrompt:
    """Test system-prompt loading from MODELS_PATH."""

    def test_returns_content_when_file_exists(self, tmp_path: Path) -> None:
        model_file = tmp_path / "test-model.md"
        model_file.write_text("You are helpful.", encoding="utf-8")

        with patch("leleka.tools.session_ops.config") as mock_config:
            mock_config.MODELS_PATH = tmp_path
            result = load_system_prompt("test-model")

        assert result == "You are helpful."

    def test_returns_none_when_file_missing(self, tmp_path: Path) -> None:
        with patch("leleka.tools.session_ops.config") as mock_config:
            mock_config.MODELS_PATH = tmp_path
            result = load_system_prompt("nonexistent-model")

        assert result is None


class TestSaveChat:
    """Test chat persistence to CHATS_PATH."""

    def test_writes_markdown_file(self, tmp_path: Path) -> None:
        messages = [
            {"role": "user", "content": "hi"},
            {"role": "assistant", "content": "hello"},
        ]

        with patch("leleka.tools.session_ops.config") as mock_config:
            mock_config.CHATS_PATH = tmp_path
            result_path = save_chat(messages, "test-model")

        assert result_path.exists()
        content = result_path.read_text(encoding="utf-8")
        assert "### User" in content
        assert "hi" in content
        assert "### Leka" in content
        assert "hello" in content

    def test_handles_special_chars_in_model_name(self, tmp_path: Path) -> None:
        with patch("leleka.tools.session_ops.config") as mock_config:
            mock_config.CHATS_PATH = tmp_path
            result_path = save_chat([{"role": "user", "content": "x"}], "ollama/mistral:7b")

        # Filename (not full path) should have no slashes or colons
        filename = result_path.name
        assert "/" not in filename
        assert ":" not in filename
