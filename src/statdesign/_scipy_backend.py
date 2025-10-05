"""Optional SciPy backend for advanced statistical distributions."""

from __future__ import annotations

import importlib
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import scipy.stats

_SCIPY_STATS: scipy.stats | None = None
_SCIPY_ERROR: Exception | None = None
_IMPORT_ATTEMPTED = False


def _attempt_scipy_import() -> None:
    """Attempt to import SciPy if enabled via environment variable or explicit request."""
    global _SCIPY_STATS, _SCIPY_ERROR, _IMPORT_ATTEMPTED

    if _IMPORT_ATTEMPTED:
        return

    _IMPORT_ATTEMPTED = True

    # Check if SciPy is explicitly disabled
    if os.environ.get("STATDESIGN_DISABLE_SCIPY", "0") == "1":
        return

    # Auto-import if enabled or if scipy extra is installed
    auto_scipy = os.environ.get("STATDESIGN_AUTO_SCIPY", "0") == "1"

    if auto_scipy:
        try:
            _SCIPY_STATS = importlib.import_module("scipy.stats")
        except ImportError as exc:
            _SCIPY_ERROR = exc


def has_scipy() -> bool:
    """Check if SciPy is available and enabled."""
    _attempt_scipy_import()
    return _SCIPY_STATS is not None


def require_scipy(feature: str) -> scipy.stats:
    """
    Require SciPy for a specific feature.

    Args:
        feature: Name of the feature requiring SciPy

    Returns:
        scipy.stats module

    Raises:
        RuntimeError: If SciPy is not available with installation instructions
    """
    _attempt_scipy_import()

    if _SCIPY_STATS is None:
        if _SCIPY_ERROR is not None:
            error_msg = f"SciPy import failed: {_SCIPY_ERROR}"
        else:
            error_msg = "SciPy is not enabled"

        raise RuntimeError(
            f"{feature} requires SciPy. {error_msg}. "
            f"Install with: pip install 'statdesign[scipy]' "
            f"or set STATDESIGN_AUTO_SCIPY=1 in an environment with SciPy."
        )

    return _SCIPY_STATS


def enable_scipy() -> bool:
    """
    Explicitly enable SciPy backend.

    Returns:
        True if SciPy was successfully enabled, False otherwise
    """
    global _SCIPY_STATS, _SCIPY_ERROR, _IMPORT_ATTEMPTED

    # Reset import state
    _IMPORT_ATTEMPTED = False
    _SCIPY_STATS = None
    _SCIPY_ERROR = None

    # Force import attempt
    try:
        _SCIPY_STATS = importlib.import_module("scipy.stats")
        _IMPORT_ATTEMPTED = True
        return True
    except ImportError as exc:
        _SCIPY_ERROR = exc
        _IMPORT_ATTEMPTED = True
        return False
