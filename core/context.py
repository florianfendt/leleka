"""
ARCHITECTURAL PURPOSE:
Provides automated workspace context extraction, normalization, and assembly pipelines.
Utilizes low-level system mapping utilities (`code2prompt_rs`) alongside LangChain
`Document` abstractions to transform flat directory states and targeted markdown specifications
into isolated prompt injection contexts for large language models.

ROADMAP & OPTIMIZATIONS:
1. Transition synchronous context building and disk operations to an asynchronous pattern (`asyncio`) to optimize multi-file rendering.
2. Abstract markdown parsing into a dedicated strategy engine supporting extended document types (e.g., restructuredText, HTML fragments).
3. Integrate localized structural validation layers to confirm path bindings before invoking external compilation processes.
"""

from pathlib import Path
from rich.console import Console
from code2prompt_rs import Code2Prompt
import logging
from pathlib import Path
from typing import List, Dict, Any
from langchain_core.documents import Document

console = Console()

def load_context_file_content(path: Path) -> str:
    """
    Architectural Purpose:
    Uses code2prompt execution to generate structured representation vectors of targeted filesystem entities.

    Input Parameters:
    - path (Path): Location of the targeted file or directory structure.

    Return Values:
    - str: Synthesized text context or structured error details.

    Side Effects / Algorithmic Logic:
    Invokes external compilation bindings; captures runtime failures as standard string returns.
    """
    try:
        c2p = Code2Prompt(path=str(path))
        rendered_object = c2p.generate()
        return rendered_object.text
    except Exception as e:
        return f"Error when generating context with code2prompt: {str(e)}"

def extract_markdown_section(file_path: Path) -> str:
    """
    Architectural Purpose:
    Extracts specialized reference blocks located within target project blueprints.

    Input Parameters:
    - file_path (Path): Target markdown file location.

    Return Values:
    - str: Isolated section payload or an empty string if criteria are unfulfilled.

    Side Effects / Algorithmic Logic:
    Reads target files into volatile memory; executes text slicing bound to specific header keys.
    """
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
    """
    Architectural Purpose:
    Iterates over extracted lists to construct unified context strings.

    Input Parameters:
    - section_text (str): Raw multi-line string text blocks containing markdown syntax.

    Return Values:
    - str: Aggregated text containing all rendered target representations.

    Side Effects / Algorithmic Logic:
    Triggers repetitive terminal output tracking alongside cascading filesystem lookups.
    """
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
    """
    Architectural Purpose:
    Coordinates structured document generation, categorical routing, and prompt context transformation workflows.
    """
    def __init__(self, workspace_root: Path):
        """
        Architectural Purpose:
        Instantiates the context engine tracking target base directories.

        Input Parameters:
        - workspace_root (Path): Root workspace absolute anchor path.

        Return Values:
        - None
        """
        self.workspace_root = workspace_root

    def load_file_as_document(self, file_path: Path) -> Document:
        """
        Architectural Purpose:
        Transforms raw target paths into formal LangChain structures enriched with classification metadata.

        Input Parameters:
        - file_path (Path): Path points target to slice and transform.

        Return Values:
        - Document: Enriched LangChain core abstraction.

        Side Effects / Algorithmic Logic:
        Performs text file reads, handles filesystem stat tracking for modification histories, and maps structural locations to categories.
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
        Architectural Purpose:
        Groups generated documents into an operational dictionary according to verified classifications.

        Input Parameters:
        - documents (List[Document]): Flat collections containing LangChain Document structures.
        - allowed_categories (List[str]): Approved classification targets.

        Return Values:
        - Dict[str, List[Document]]: Key-mapped categorized structural storage structures.

        Side Effects / Algorithmic Logic:
        None. Pure in-memory reference sorting operation.
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
        Architectural Purpose:
        Flattens multi-layered Document frameworks into uniform string context streams optimized for LLM consumption.

        Input Parameters:
        - documents (List[Document]): target document collections for final transformations.

        Return Values:
        - str: Unified prompt injection block containing clean separation elements.

        Side Effects / Algorithmic Logic:
        Iterates over input instances to join page data streams separated by systemic headers.
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