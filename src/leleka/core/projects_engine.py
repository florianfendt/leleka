from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
import re

@dataclass
class ProjectFile:
    """Kapselt ein Markdown-File, das einer strikten Überschriften-Struktur folgt."""
    filepath: Path
    template_path: Path
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
        """Extrahiert alle Überschriften aus dem Template als Source of Truth."""
        if not self.template_path or not self.template_path.is_file():
            return []

        content = self.template_path.read_text(encoding="utf-8")
        # Findet Zeilen, die mit # starten (z.B. # Titel, ## Kapitel)
        return [line.strip() for line in content.splitlines() if line.startswith("#")]

    def parse(self) -> None:
        """Zerlegt die Datei in ihre Kapitel basierend auf den Überschriften."""
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
        """Gibt den Inhalt eines spezifischen Kapitels zurück."""
        return self._sections.get(header, "")

    def update_chapter(self, header: str, new_content: str) -> None:
        """Updates oder erstellt den Inhalt eines Kapitels im Arbeitsspeicher."""
        self._sections[header] = new_content.strip()

    def delete_chapter(self, header: str) -> None:
        """Löscht ein Kapitel aus der Struktur."""
        if header in self._sections:
            del self._sections[header]

    def save(self) -> None:
        """Schreibt die gesamte Struktur geordnet zurück in die Datei."""
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