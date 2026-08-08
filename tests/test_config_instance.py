"""Regression tests for config module-level singleton."""

from pathlib import Path

import pytest


class TestConfigInstanceNotModule:
    """Ensure _cfg is the _Config instance, not a Python module.

    Previously ``from leleka import config`` returned the *module*
    ``leleka.config`` (submodule shadowing) instead of the ``_Config()``
    instance — causing ``AttributeError: 'module' object has no attribute
    'MODELS_PATH'`` at runtime.

    This test guards against that regression by verifying the import path
    returns an instance, not a module.
    """

    def test_cfg_is_instance_not_module(self) -> None:
        from leleka.config import _cfg  # noqa: F401

        assert hasattr(_cfg, "MODELS_PATH"), (
            "_cfg must be the _Config instance; if you see this error, "
            "submodule shadowing has returned — 'from leleka import config' "
            "is returning a module instead of the singleton."
        )

    def test_cfg_has_required_attributes(self) -> None:
        from leleka.config import _cfg  # noqa: F401

        assert hasattr(_cfg, "CONTEXT_PATH")
        assert hasattr(_cfg, "CHATS_PATH")
        assert hasattr(_cfg, "MODELS_PATH")
        assert hasattr(_cfg, "DEFAULT_MODEL")

    def test_paths_are_pathlib_objects(self) -> None:
        from leleka.config import _cfg  # noqa: F401

        assert isinstance(_cfg.CONTEXT_PATH, Path)
        assert isinstance(_cfg.CHATS_PATH, Path)
        assert isinstance(_cfg.MODELS_PATH, Path)


class TestDefaultModelOnInstance:
    """Ensure DEFAULT_MODEL is accessible via the instance."""

    def test_default_model_via_instance(self) -> None:
        from leleka.config import _cfg  # noqa: F401

        assert hasattr(_cfg, "DEFAULT_MODEL")
        assert _cfg.DEFAULT_MODEL == "gemma4:12b"


class TestLelekaLogoAvailable:
    """Ensure LELEKA_LOGO is available as a module-level constant."""

    def test_leleka_logo_is_string(self) -> None:
        from leleka.config import LELEKA_LOGO  # noqa: F401

        assert isinstance(LELEKA_LOGO, str)
        assert len(LELEKA_LOGO) > 0
