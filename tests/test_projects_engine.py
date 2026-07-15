"""Tests for ``core.projects_engine.ProjectFile``."""

from pathlib import Path

import pytest

from leleka.core.projects_engine import ProjectFile


class TestProjectFileInit:
    """Test __post_init__ behaviour (file parsing on construction)."""

    def test_parses_existing_file(self, tmp_path: Path) -> None:
        doc = tmp_path / "doc.md"
        doc.write_text("# Title\n\n## Abstract\nHello world\n", encoding="utf-8")

        pf = ProjectFile(filepath=doc, template_path=None)

        assert pf.get_chapter("## Abstract") == "Hello world"

    def test_empty_sections_when_file_missing(self, tmp_path: Path) -> None:
        doc = tmp_path / "missing.md"  # does not exist

        pf = ProjectFile(filepath=doc, template_path=None)

        assert pf._sections == {}


class TestProjectFileCRUD:
    """Test chapter read/update/delete/save round-trip."""

    def test_update_chapter_creates_new(self, tmp_path: Path) -> None:
        doc = tmp_path / "doc.md"
        doc.write_text("# Title\n", encoding="utf-8")

        pf = ProjectFile(filepath=doc, template_path=None)
        pf.update_chapter("## New", "content")

        assert pf.get_chapter("## New") == "content"

    def test_delete_chapter(self, tmp_path: Path) -> None:
        doc = tmp_path / "doc.md"
        doc.write_text("# Title\n\n## ToDelete\nbye\n", encoding="utf-8")

        pf = ProjectFile(filepath=doc, template_path=None)
        pf.delete_chapter("## ToDelete")

        assert pf.get_chapter("## ToDelete") == ""

    def test_save_respects_template_order(self, tmp_path: Path) -> None:
        tpl = tmp_path / "tpl.md"
        tpl.write_text("# Title\n\n## B\n\n## A\n", encoding="utf-8")

        doc = tmp_path / "doc.md"
        doc.write_text("# Title\n\n## A\nalpha\n\n## B\nbeta\n", encoding="utf-8")

        pf = ProjectFile(filepath=doc, template_path=tpl)
        # Update order: swap so A comes before B in content
        pf.update_chapter("## A", "ALPHA")
        pf.update_chapter("## B", "BETA")
        pf.save()

        written = doc.read_text(encoding="utf-8")
        # Template order is B then A, so B should appear first after "# Title"
        assert written.index("## B") < written.index("## A")

    def test_save_writes_new_chapter(self, tmp_path: Path) -> None:
        doc = tmp_path / "doc.md"
        doc.write_text("# Title\n", encoding="utf-8")

        pf = ProjectFile(filepath=doc, template_path=None)
        pf.update_chapter("## Extra", "extra content")
        pf.save()

        assert "## Extra" in doc.read_text(encoding="utf-8")


class TestGetTemplateHeaders:
    """Test that headings are extracted from a template file."""

    def test_returns_headings(self, tmp_path: Path) -> None:
        tpl = tmp_path / "tpl.md"
        tpl.write_text("# H1\n## H2\n### H3\nplain text\n", encoding="utf-8")

        pf = ProjectFile(filepath=tmp_path / "x.md", template_path=tpl)

        headers = pf.get_template_headers()
        assert "# H1" in headers
        assert "## H2" in headers
        assert "### H3" in headers
        assert "plain text" not in headers

    def test_returns_empty_when_no_template(self, tmp_path: Path) -> None:
        pf = ProjectFile(filepath=tmp_path / "x.md", template_path=None)
        assert pf.get_template_headers() == []
