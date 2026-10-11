"""All of Keebo's animations. Importing this package registers them."""
from __future__ import annotations

_loaded = False


def load_all() -> None:
    global _loaded
    if _loaded:
        return
    _loaded = True
    from ..scenes import load_all as load_scenes
    from . import states  # noqa: F401

    load_scenes()
    _load_plugins()


def _load_plugins() -> None:
    """Import ``~/.keebo/plugins/*.py`` so users can add animations without forking."""
    import importlib.util
    import logging

    from ..engine.progression import home

    folder = home() / "plugins"
    if not folder.is_dir():
        return
    for path in sorted(folder.glob("*.py")):
        try:
            spec = importlib.util.spec_from_file_location("keebo_plugin_" + path.stem, path)
            if spec and spec.loader:
                spec.loader.exec_module(importlib.util.module_from_spec(spec))
        except Exception as e:  # noqa: BLE001 - a broken plugin must not kill Keebo
            logging.getLogger("keebo").warning("plugin %s failed: %s", path.name, e)


from .base import REGISTRY, Clip, Look, animation, build, get, names  # noqa: E402

__all__ = ["REGISTRY", "Clip", "Look", "animation", "build", "get", "names", "load_all"]
