from pathlib import Path
from rich.console import Console
from code2prompt_rs import Code2Prompt
import logging
from pathlib import Path
from typing import List, Dict, Any
from langchain_core.documents import Document

console = Console()

def load_context_file_content(path: Path) -> str:
    """Rendert den Datei- oder Ordnerinhalt mithilfe von code2prompt."""
    try:
        c2p = Code2Prompt(path=str(path))
        rendered_object = c2p.generate()
        return rendered_object.text
    except Exception as e:
        return f"Error when generating context with code2prompt: {str(e)}"

def extract_markdown_section(file_path: Path) -> str:
    """Extrahiert den Referenz-Abschnitt aus Projektdateien."""
    if not file_path.exists():
        return ""
    text = file_path.read_text(encoding="utf-8")
    if "02 references" not in text:
        return ""
    parts = text.split("02 references", 1)
    if len(parts) < 2:
        return ""
    section = parts[1]
    if "\n##" in section:
        return section.split("\n##", 1)[0].strip()
    return section.strip()

def parse_and_execute_bullet_points(section_text: str) -> str:
    """Liest die Bulletpoints ein und sammelt das Feedback im Terminal."""
    cleaned_paths = [
        line.lstrip("*- ").strip()
        for line in section_text.splitlines()
        if line.strip().startswith(("*", "-"))
    ]
    combined_context = ""
    for path_str in cleaned_paths:
        console.print(f"[dim]Lade Datei in Kontext: {path_str}[/dim]")
        result = load_context_file_content(Path(path_str))
        combined_context += result
    return combined_context


# Wenn du spezifische Loader brauchst, sobald sie installiert sind:
# from langchain_community.document_loaders import TextLoader, CSVLoader

logger = logging.getLogger("leleka.core.context_engine")

class LocalContextEngine:
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root

    def load_file_as_document(self, file_path: Path) -> Document:
        """
        Lädt eine Datei und konvertiert sie in ein LangChain Document-Objekt.
        Extrahiert automatisch erste Metadaten basierend auf der Verzeichnisstruktur.
        """
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            logger.error(f"Fehler beim Lesen von {file_path}: {e}")
            content = ""

        # Automatische Kategorisierung anhand des Ordnernamens im Repo
        # z.B. "01_ai_stack" -> "ai_stack" oder "02_scripts" -> "scripts"
        category = "general"
        if file_path.is_relative_to(self.workspace_root):
            relative_parts = file_path.relative_to(self.workspace_root).parts
            if len(relative_parts) > 1:
                category = relative_parts[0].lower()
                # Bereinige führende Zahlen (z.B. "03_dev" -> "dev")
                category = category.split('_', 1)[-1] if '_' in category else category

        # Hier mappen wir die Daten in das standardisierte LangChain-Schema
        metadata = {
            "source": str(file_path),
            "file_name": file_path.name,
            "extension": file_path.suffix.lstrip('.'),
            "category": category,
            "last_modified": file_path.stat().st_mtime if file_path.exists() else 0
        }

        return Document(page_content=content, metadata=metadata)

    def filter_and_categorize(self, documents: List[Document], allowed_categories: List[str]) -> Dict[str, List[Document]]:
        """
        Sortiert die geladenen Dokumente in ein Dictionary nach Kategorien auf,
        um der CLI die gezielte Auswahl zu ermöglichen (z.B. nur 'dev' oder 'ai_stack').
        """
        categorized: Dict[str, List[Document]] = {cat: [] for cat in allowed_categories}
        categorized["other"] = []

        for doc in documents:
            cat = doc.metadata.get("category", "other")
            if cat in categorized:
                categorized[cat].append(doc)
            else:
                categorized["other"].append(doc)

        return categorized

    def prepare_prompt_context(self, documents: List[Document]) -> str:
        """
        Formatiert die LangChain Dokumente final für deinen LLM-Prompt.
        Nutzt die Metadaten für saubere Trennung.
        """
        formatted_chunks = []
        for doc in documents:
            meta = doc.metadata
            formatted_chunks.append(f"### [SYSTEM-CONTEXT] CATEGORY: {meta['category'].upper()} | FILE: {meta['file_name']}")
            formatted_chunks.append(f"Path: {meta['source']}\n")

            # Hier greift später deine abgetrennte Markdown-Logik (z.B. shift_headings)
            formatted_chunks.append(doc.page_content)
            formatted_chunks.append("\n---")

        return "\n\n".join(formatted_chunks)