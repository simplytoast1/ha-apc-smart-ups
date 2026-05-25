"""Pytest fixtures: import the integration package without booting Home Assistant.

Most of the unit-testable surface (SNMP value coercion, OID table,
enum-mapping) is pure Python with no HA dependency. We bootstrap the
package by hand so these tests run with just ``pytest`` and the
``pysnmp`` runtime requirement - no ``pytest-homeassistant-custom-component``
needed.
"""
from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_PKG_DIR = _ROOT / "custom_components" / "apc_smart_ups"


def _load(name: str) -> types.ModuleType:
    """Load apc_smart_ups.<name> without running the package __init__."""
    full = f"apc_smart_ups.{name}"
    if full in sys.modules:
        return sys.modules[full]
    if "apc_smart_ups" not in sys.modules:
        pkg = types.ModuleType("apc_smart_ups")
        pkg.__path__ = [str(_PKG_DIR)]
        sys.modules["apc_smart_ups"] = pkg
    spec = importlib.util.spec_from_file_location(full, _PKG_DIR / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[full] = mod
    spec.loader.exec_module(mod)
    return mod


# Load the modules we'll be testing once, at session start.
_load("const")
_load("oids")
_load("snmp_client")
