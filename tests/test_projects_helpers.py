"""Tests for ``tools.projects_helpers``."""

from leleka.tools.projects_helpers import calc_token_stats, log_sys_pulse


class TestCalcTokenStats:
    """Test token-stats calculation from Ollama response chunks."""

    def test_parses_standard_chunk(self, sample_done_chunk: dict[str, object]) -> None:
        stats = calc_token_stats(sample_done_chunk)

        assert isinstance(stats["context"], int)
        assert isinstance(stats["response"], int)
        assert isinstance(stats["context_size"], int)
        assert stats["context"] == 256
        assert stats["response"] == 128
        assert stats["context_size"] == 8_192

    def test_defaults_on_missing_keys(self) -> None:
        empty_chunk: dict[str, object] = {"done": True}

        stats = calc_token_stats(empty_chunk)

        assert stats["context"] == 0
        assert stats["response"] == 0
        assert stats["context_size"] == 8_192


class TestLogSysPulse:
    """Test system-pulse payload construction."""

    def test_returns_expected_payload(self) -> None:
        result = log_sys_pulse("proj-1", "web", "A web app")

        assert result["project_id"] == "proj-1"
        assert result["project_type"] == "web"
        assert result["abstract"] == "A web app"

    def test_payload_is_independent_copy(self) -> None:
        payload_a = log_sys_pulse("a", "x", "xa")
        payload_b = log_sys_pulse("b", "y", "yb")

        assert payload_a is not payload_b
        assert payload_a["project_id"] != payload_b["project_id"]
