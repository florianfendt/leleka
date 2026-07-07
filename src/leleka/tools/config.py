import os
from pathlib import Path

# 📍 Ermittelt den absoluten Pfad zu diesem Skript (src/leleka/tools/)
# und geht zwei Ordner nach oben zum Projekt-Root (leleka/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

# --- UMGEBUNGSVARIABLEN & PFADE ---
# Basis-Kontext-Verzeichnis (Falls Umgebungsvariable fehlt, nutzen wir das Projekt-Root)
CONTEXT_PATH = Path(os.environ.get("CONTEXT", PROJECT_ROOT))
CHATS_PATH = CONTEXT_PATH / "chats"

# Pfad zu den System-Prompts / Markdown-Modellen (Immer relativ zum Projekt-Root verankert!)
MODELS_PATH = Path(os.environ.get("MODELS", PROJECT_ROOT / "models"))
DEFAULT_MODEL = "mistral:7b"

# --- DESIGN & UI ---
# Das zentrale Leleka-Logo
LELEKA_LOGO = r"""
[bold magenta]       __ [/bold magenta]
[bold magenta]  ___ / /__ ___ ____  ___ _ [/bold magenta]
[bold magenta] / _ / / -_) _ `/ _ \/ _ `/ [/bold magenta]
[bold magenta] \___/_/\__/\_,_/\___/\_,_/ [/bold magenta]
[bold white] >> The Stork is watching... << [/bold white]
"""