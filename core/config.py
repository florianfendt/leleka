import json
from pathlib import Path
from typing import Dict, Any

# 1. Zeigt jetzt absolut korrekt auf deine paths.json
CONFIGS_PATH = Path("~/workspace/00_system/config/paths.json").expanduser()


def load_config() -> Dict[str, Any]:
    """Loads the central JSON paths configuration."""
    if not CONFIGS_PATH.exists():
        return {"paths": {}, "targets": {}}
    try:
        with open(CONFIGS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"paths": {}, "targets": {}}


def extract_and_inject_paths(data: Dict[str, Any], target_globals: Dict[str, Any]) -> None:
    """Parses paths and targets from paths.json and injects them as UPPERCASE variables."""
    # Wir holen uns den Workspace-Root als Anker
    paths_block = data.get("paths", {})
    workspace_raw = paths_block.get("workspace", {}).get("path", ".")
    workspace_root = Path("~/workspace").expanduser() if workspace_raw == "." else Path(workspace_raw).expanduser()

    for category in ["paths", "targets"]:
        sub_dict = data.get(category, {})
        for key, info in sub_dict.items():
            if isinstance(info, dict) and "path" in info:
                raw_path = info["path"]
                if raw_path == ".":
                    resolved_path = workspace_root.resolve()
                else:
                    resolved_path = (workspace_root / raw_path).resolve()

                # In den globalen Scope injizieren (z.B. roles -> ROLES)
                target_globals[key.upper()] = resolved_path


# Ausführen des Parsers
RAW_CONFIG = load_config()
extract_and_inject_paths(RAW_CONFIG, globals())

# # =====================================================================
# # 2. STRICKTE EXPORTE (Garantiert, dass der Import in ai_commands.py klappt!)
# # =====================================================================
# WORKSPACE_ROOT = globals().get("WORKSPACE", Path("~/workspace").expanduser().resolve())

# # Hier holen wir die Variablen ab – falls die JSON hakt, greift der sichere Fallback
# ROLES = globals().get("ROLES", WORKSPACE_ROOT / "01_ai_stack/models")
# PROJECTS = globals().get("PROJECTS", WORKSPACE_ROOT / "03_dev")
# LOGS = globals().get("LOGS", WORKSPACE_ROOT / "00_system/99_logs")
# CONTEXT = globals().get("CONTEXT", WORKSPACE_ROOT / "01_ai_stack/context")
# PULSE = globals().get("PULSE", WORKSPACE_ROOT / "00_system/system_pulse.csv")

# MAC_ADDRESSES = {
#     "bradley": "70:20:84:0e:84:35",
#     "ferrari": "38:f7:cd:c6:cc:44"
# }

# # Kompatibilität für den Import-Befehl
# ROLES_PATH = ROLES
# PROJECTS_PATH = PROJECTS
# CONTEXT_PATH = CONTEXT