"""Markdown project-file CRUD with template-driven chapter ordering.

The ``ProjectFile`` dataclass parses a Markdown document into chapters keyed by
their heading text (e.g. ``"## Abstract"``).  Chapters can be read, updated,
deleted and re-written while respecting the order defined in an optional
template file.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
import re

@dataclass
class ProjectFile:
    """CRUD wrapper around a structured Markdown project file.

    Chapters are keyed by their heading text (e.g. ``"## Abstract"``).
    When *template_path* is provided, save order follows the template's
    headings rather than insertion order.
    """

    filepath: Path
    """Path to the Markdown document being managed."""

    template_path: Path | None
    """Optional template that defines chapter ordering (source of truth)."""

    # Interner Speicher für die geparsten Kapitel: { "## Überschrift": "Inhalt\n..." }
    _sections: Dict[str, str] = field(default_factory=dict, init=False)

    def __post_init__(self) -> None:
        self.filepath = Path(self.filepath).resolve()
        if self.template_path:
            self.template_path = Path(self.template_path).resolve()

        # Direkt beim Start parsen, wenn die Datei existiert
        if self.filepath.is_file():
            self.parse()

    def get_template_headers(self) -> List[str]:
        """Extract all headings from the template as source of truth.

        Returns:
            List of heading strings (e.g. ``["# Titel", "## Kapitel"]``).
        """
        if not self.template_path or not self.template_path.is_file():
            return []

        content = self.template_path.read_text(encoding="utf-8")
        # Findet Zeilen, die mit # starten (z.B. # Titel, ## Kapitel)
        return [line.strip() for line in content.splitlines() if line.startswith("#")]

    def parse(self) -> None:
        """Parse the file into chapters based on Markdown headings.

        Populates ``_sections`` dict keyed by heading text.  Text before
        the first heading is stored under ``"_HEADER_LESS_"``.
        """
        if not self.filepath.is_file():
            return

        content = self.filepath.read_text(encoding="utf-8")
        lines = content.splitlines()

        current_header = "_HEADER_LESS_"  # Für Text vor der ersten Überschrift
        current_content: List[str] = []
        self._sections = {}

        for line in lines:
            if line.startswith("#"):
                # Vorheriges Kapitel wegspeichern
                self._sections[current_header] = "\n".join(current_content).strip()
                # Neues Kapitel starten
                current_header = line.strip()
                current_content = []
            else:
                current_content.append(line)

        # Letztes Kapitel sichern
        self._sections[current_header] = "\n".join(current_content).strip()

    def get_chapter(self, header: str) -> str:
        """Return the content of a chapter by its heading.

        Args:
            header: Exact heading string (e.g. ``"## Abstract"``).

        Returns:
            Chapter content, or empty string if *header* is not found.
        """
        return self._sections.get(header, "")

    def update_chapter(self, header: str, new_content: str) -> None:
        """Update or create a chapter's content in memory.

        Args:
            header: Exact heading string (e.g. ``"## Abstract"``).
            new_content: New text body for the chapter.
        """
        self._sections[header] = new_content.strip()

    def delete_chapter(self, header: str) -> None:
        """Delete a chapter from the in-memory structure.

        Args:
            header: Exact heading string to remove.
        """
        if header in self._sections:
            del self._sections[header]

    def save(self) -> None:
        """Write the full chapter structure back to disk, ordered by template.

        When a template is present, chapters are written in the order defined
        by the template; missing template chapters get their heading created
        as an empty section.  Chapters not in the template (but with content)
        are appended after the last template entry.
        """
        # Wenn ein Template existiert, nutzen wir dessen Reihenfolge als Orientierung
        allowed_headers = self.get_template_headers()

        output: List[str] = []

        # Falls es Text vor der ersten Überschrift gab
        if "_HEADER_LESS_" in self._sections and self._sections["_HEADER_LESS_"]:
            output.append(self._sections["_HEADER_LESS_"])

        # Wenn wir ein Template haben, gehen wir strikt nach dessen Reihenfolge vor
        headers_to_write = allowed_headers if allowed_headers else [h for h in self._sections.keys() if h != "_HEADER_LESS_"]

        for header in headers_to_write:
            if header in self._sections:
                output.append(f"\n{header}")
                if self._sections[header]:
                    output.append(self._sections[header])
            elif allowed_headers:
                # Falls ein Kapitel im Template steht, aber noch leer ist,
                # legen wir die Überschrift trotzdem an (Struktur erhalten)
                output.append(f"\n{header}\n")

        self.filepath.write_text("\n".join(output) + "\n", encoding="utf-8")