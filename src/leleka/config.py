import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# --- PATHS ---
# Basis-Kontext-Verzeichnis (Falls Umgebungsvariable fehlt, nutzen wir das Projekt-Root)
CONTEXT_PATH = Path(os.environ.get("CONTEXT", PROJECT_ROOT))
CHATS_PATH = CONTEXT_PATH / "chats"
MODELS_PATH = Path(os.environ.get("MODELS", PROJECT_ROOT / "models"))
DEFAULT_MODEL = "mistral:7b"
# Aus dem Pfad direkt den Text auslesen
LOGO_PATH = PROJECT_ROOT / "templates" / "leleka_logo.md"
LELEKA_LOGO = LOGO_PATH.read_text(encoding="utf-8")
