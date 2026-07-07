"""
file_name: workspace_ops.py
description: Core I/O operations for context scraping and directory management.
"""

import csv
import logging
from pathlib import Path
from typing import List, Dict

# Import der bereinigten Markdown-Tools aus dem gleichen Verzeichnis
from .markdown_utils import shift_headings, wrap_in_code_block

logger = logging.getLogger("leleka.tools.workspace_ops")

def csv_to_md(csv_path: Path) -> str:
    """Liest eine CSV-Datei und nutzt markdown_utils für den Codeblock."""
    if not csv_path.exists():
        return ""
    try:
        raw_content = csv_path.read_text(encoding='utf-8')
        return wrap_in_code_block(raw_content, "csv")
    except Exception as e:
        logger.error(f"Fehler bei CSV-Verarbeitung {csv_path.name}: {e}")
        return ""

def append_to_csv(file_path: Path, data: Dict[str, str], mapping_cols: List[str]) -> bool:
    """Schreibt Daten zeilenweise in eine CSV (z.B. für den System-Pulse)."""
    try:
        file_exists = file_path.exists()
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=mapping_cols)
            if not file_exists:
                writer.writeheader()
            writer.writerow(data)
        return True
    except Exception as e:
        logger.error(f"Fehler beim Schreiben in CSV {file_path}: {e}")
        return False

def scrape_context_from_files(source_files: List[Path]) -> str:
    """Aggregiert Dateiinhalte zu einem strukturierten Kontext-String."""
    context_chunks = []

    for src_path in source_files:
        if not src_path.exists():
            logger.warning(f"Quelle nicht gefunden: {src_path}")
            continue

        logger.info(f"Scraping context from: {src_path.name}")
        context_chunks.append(f"## SOURCE: {src_path.name}\n")

        try:
            if src_path.suffix == '.csv':
                context_chunks.append(csv_to_md(src_path))
            elif src_path.suffix == '.json':
                raw_json = src_path.read_text(encoding='utf-8')
                context_chunks.append(wrap_in_code_block(raw_json, "json"))
            else:
                content = src_path.read_text(encoding='utf-8')
                if src_path.suffix == '.md':
                    context_chunks.append(shift_headings(content))
                else:
                    # Python-Code, Logs etc. im passenden Code-Block kapseln
                    lang = src_path.suffix.lstrip('.') or "text"
                    context_chunks.append(wrap_in_code_block(content, lang))

            context_chunks.append("\n\n---\n\n")
        except Exception as e:
            logger.error(f"Fehler beim Scrapen von {src_path.name}: {e}")

    return "".join(context_chunks)

def smart_mirror_directory(src_dir: Path, dest_dir: Path) -> None:
    """Spiegelt ein Verzeichnis und wirft alte Leichen im Ziel raus."""
    import shutil
    if not src_dir.exists():
        return

    dest_dir.mkdir(parents=True, exist_ok=True)

    # 1. Sync
    for item in src_dir.glob('*'):
        target_item = dest_dir / item.name
        if item.is_file():
            shutil.copy2(item, target_item)
        elif item.is_dir():
            shutil.copytree(item, target_item, dirs_exist_ok=True)

    # 2. Pruning
    for item in dest_dir.iterdir():
        if not (src_dir / item.name).exists():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)