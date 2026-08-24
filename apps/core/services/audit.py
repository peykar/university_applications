"""Backward-compatible imports for audit helpers.

The canonical implementation lives in :mod:`apps.core.audit`.
"""

from apps.core.audit import (
    audited_get_or_create,
    audited_update_or_create,
    get_system_user,
)

__all__ = [
    "audited_get_or_create",
    "audited_update_or_create",
    "get_system_user",
]
