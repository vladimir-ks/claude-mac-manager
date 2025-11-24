"""
Safety module for Claude Mac Manager.

Implements multi-layer protection system to prevent accidental data loss:
- Layer 1: Protected path whitelist/blacklist
- Layer 2: Category-based permissions
- Layer 3: Dry-run default mode
- Layer 4: Trash-based deletion
- Layer 5: Comprehensive audit logging
- Layer 6: Permission validation

All safety-critical code in this module requires 100% test coverage.
"""

from .protected_paths import (
    PROTECTED_PATHS,
    is_protected_path,
    validate_path_safety,
    ProtectedPathError,
)

from .validator import (
    validate_deletion,
    DeletionValidator,
    ValidationError,
)

__all__ = [
    # Protected paths
    "PROTECTED_PATHS",
    "is_protected_path",
    "validate_path_safety",
    "ProtectedPathError",
    # Validation
    "validate_deletion",
    "DeletionValidator",
    "ValidationError",
]
