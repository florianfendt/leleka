"""Tests for ``tools.ps_helpers`` pure helpers."""

from io import StringIO

from rich.console import Console

from leleka.tools import ps_helpers
from leleka.tools.ps_helpers import _format_size, _model_time


class TestFormatSize:
    """Test byte → human-readable conversion."""

    def test_bytes(self) -> None:
        assert _format_size(500) == "500.0 B"

    def test_kilobytes(self) -> None:
        assert _format_size(1024) == "1.0 KB"

    def test_megabytes(self) -> None:
        assert _format_size(1_048_576) == "1.0 MB"

    def test_gigabytes(self) -> None:
        assert _format_size(1_073_741_824) == "1.0 GB"

    def test_terabytes(self) -> None:
        assert _format_size(1_099_511_627_776) == "1.0 TB"

    def test_exceeds_tb_returns_pb(self) -> None:
        result = _format_size(1_099_511_627_776 * 2048)
        assert result.endswith("PB")


class TestModelTime:
    """Test ISO timestamp → formatted date conversion."""

    def test_parses_iso_timestamp(self) -> None:
        result = _model_time("2024-02-14T10:15:30.123456Z")
        assert result == "14.02.2024 10:15"

    def test_returns_raw_when_no_t_separator(self) -> None:
        assert _model_time("3 weeks ago") == "3 weeks ago"

    def test_handles_question_mark(self) -> None:
        assert _model_time("?") == "?"

    def test_handles_empty_string(self) -> None:
        # Empty string is falsy → returns "?" per the function's guard clause
        assert _model_time("") == "?"


def test_show_system_pulse_reads_pulse_environment(monkeypatch, tmp_path) -> None:
    pulse_file = tmp_path / "pulse.json"
    pulse_file.write_text("{}", encoding="utf-8")
    monkeypatch.setenv("PULSE", str(pulse_file))
    output = StringIO()
    monkeypatch.setattr(ps_helpers, "console", Console(file=output, color_system=None))

    ps_helpers.show_system_pulse()

    assert "erfolgreich geladen" in output.getvalue()
