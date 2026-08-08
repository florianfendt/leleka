"""Configuration for leleka — lazy-loaded paths from shared paths.json."""

import functools
import json
import os
from pathlib import Path
from typing import Any, Dict

# ---------------------------------------------------------------------------
# Import spiderweb's PathEngine (sibling project under /home/flo/02_dev/)
# ---------------------------------------------------------------------------
_SPIDERWEB_SRC = "/home/flo/02_dev/spiderweb/src"
if _SPIDERWEB_SRC not in __import__("sys").path:
    __import__("sys").path.insert(0, _SPIDERWEB_SRC)

from spiderweb.core.paths_engine import PathEngine  # noqa: E402

# ---------------------------------------------------------------------------
# Paths JSON location — env var overrides the default shared location
# ---------------------------------------------------------------------------
_DEFAULT_PATHS_JSON = str(Path(__file__).resolve().parent.parent.parent / "paths.json")


def _load_paths_json() -> Dict[str, Any]:
    """Load and return paths.json from PATHS_JSON env or the default."""
    path_str = os.environ.get("PATHS_JSON", _DEFAULT_PATHS_JSON)
    raw = Path(path_str).read_text(encoding="utf-8")
    data = json.loads(raw)

    # Validate that required categories exist
    for cat in ("paths", "targets"):
        if cat not in data:
            raise ValueError(f"paths.json missing required category: '{cat}'")

    return data


# ---------------------------------------------------------------------------
# Config class — lazy-loaded, validated paths
# ---------------------------------------------------------------------------

class _Config:
    """Lazy configuration with runtime validation.

    Paths are resolved from spiderweb's shared ``paths.json`` via PathEngine
    on first access (cached).  Leleka-specific derived paths such as
    CHATS_PATH are computed after resolution.
    """

    DEFAULT_MODEL = "gemma4:12b"

    def __init__(self) -> None:
        self._engine: PathEngine | None = None
        self._resolved: bool = False

    # -- public path properties -------------------------------------------

    @functools.cached_property  # type: ignore[attr-defined]
    def CONTEXT_PATH(self) -> Path:
        """Central dropzone for ready-to-deploy context .md files."""
        return self._ensure_resolved()["CONTEXT"]

    @functools.cached_property  # type: ignore[attr-defined]
    def CHATS_PATH(self) -> Path:
        """Leleka-specific chat history directory (derived)."""
        return self.CONTEXT_PATH / "chats"

    @functools.cached_property  # type: ignore[attr-defined]
    def MODELS_PATH(self) -> Path:
        """Modelfiles directory."""
        return self._ensure_resolved()["MODELS"]

    # -- internal ---------------------------------------------------------

    def _ensure_resolved(self) -> Dict[str, str]:
        if not self._resolved:
            data = _load_paths_json()
            engine = PathEngine(data)
            resolved = engine.resolve_hierarchy()  # type: ignore[return-value]

            # Normalize keys to lowercase for robust matching
            normalized_resolved = {k.lower(): v for k, v in resolved.items()}

            mapping: Dict[str, Path] = {}
            for key in ("context", "models"):
                if key in normalized_resolved:
                    mapping[key.upper()] = Path(normalized_resolved[key])

            self._engine = engine
            self._resolved_paths = mapping
            self._resolved = True

        return self._resolved_paths

    def reload(self) -> None:
        """Invalidate all cached paths — useful for testing / hot-reload."""
        self._engine = None
        self._resolved = False
        attrs_to_clear = ("CONTEXT_PATH", "CHATS_PATH", "MODELS_PATH")
        for attr in attrs_to_clear:
            try:
                delattr(self, attr)  # type: ignore[arg-type]
            except AttributeError:
                pass


# ---------------------------------------------------------------------------
# Module-level singleton — callers use ``_cfg.CONTEXT_PATH`` etc.
# ---------------------------------------------------------------------------

_cfg = _Config()

DEFAULT_MODEL = "gemma4:12b"

LOGO_PATH = Path(__file__).resolve().parent / "templates" / "leleka_logo.md"
try:
    LELEKA_LOGO = LOGO_PATH.read_text(encoding="utf-8")
except (FileNotFoundError, IOError):
    LELEKA_LOGO = "[bold magenta]>> Leleka CLI <<[/bold magenta]"
