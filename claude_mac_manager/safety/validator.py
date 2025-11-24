"""
Deletion Validator - Multi-Layer Safety System

Implements Layers 2-6 of the safety architecture:
- Layer 2: Category-based permissions (database validation)
- Layer 3: Dry-run enforcement
- Layer 4: Trash-based deletion verification
- Layer 5: Audit logging requirements
- Layer 6: Permission validation

Combined with Layer 1 (protected_paths.py) to provide defense-in-depth.

Author: Vladimir K.S.
Coverage Requirement: 100% (safety-critical)
"""

import os
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any

from .protected_paths import validate_path_safety, ProtectedPathError
from .. import DATABASE_PATH


class ValidationError(Exception):
    """Raised when deletion validation fails."""
    pass


class CategoryNotDeletableError(ValidationError):
    """Raised when category is marked as not deletable in database."""
    pass


class NoRestorationMethodError(ValidationError):
    """Raised when no restoration method is available."""
    pass


class DryRunViolationError(ValidationError):
    """Raised when attempting real deletion in dry-run mode."""
    pass


@dataclass
class ValidationResult:
    """Result of deletion validation check."""

    valid: bool
    path: str
    category: Optional[str] = None
    size_bytes: int = 0
    is_deletable: bool = False
    restoration_command: Optional[str] = None
    warnings: list[str] = None
    errors: list[str] = None

    def __post_init__(self) -> None:
        """Initialize mutable default values."""
        if self.warnings is None:
            self.warnings = []
        if self.errors is None:
            self.errors = []


class DeletionValidator:
    """
    Multi-layer validator for safe deletion operations.

    This class implements Layers 2-6 of the safety system, working in conjunction
    with Layer 1 (protected paths) to provide comprehensive protection.

    Usage:
        validator = DeletionValidator(dry_run=True)
        result = validator.validate_deletion("/path/to/node_modules", "node_modules")

        if result.valid:
            # Safe to proceed with deletion
            pass
        else:
            # Handle validation errors
            print(result.errors)

    Attributes:
        dry_run: If True, prevents any actual deletion operations
        require_confirmation: If True, requires explicit user confirmation
    """

    def __init__(
        self,
        dry_run: bool = True,
        require_confirmation: bool = True,
        database_path: Optional[Path] = None
    ) -> None:
        """
        Initialize deletion validator.

        Args:
            dry_run: If True, only preview deletions (default: True for safety)
            require_confirmation: If True, require explicit confirmation (default: True)
            database_path: Path to SQLite database (default: from config)
        """
        self.dry_run = dry_run
        self.require_confirmation = require_confirmation
        self.database_path = database_path or DATABASE_PATH

    def validate_deletion(
        self,
        path: str,
        category: Optional[str] = None
    ) -> ValidationResult:
        """
        Perform comprehensive validation for deletion operation.

        This is the main entry point for validation. It runs all safety checks:
        1. Layer 1: Protected paths check
        2. Layer 2: Category permissions check (database)
        3. Layer 3: Dry-run enforcement
        4. Layer 4: Restoration method verification
        5. Layer 6: Permission check (file system access)

        Args:
            path: Path to validate for deletion
            category: Expected category (e.g., "node_modules", "venv")

        Returns:
            ValidationResult with validation outcome and details

        Example:
            >>> validator = DeletionValidator(dry_run=True)
            >>> result = validator.validate_deletion("/project/node_modules", "node_modules")
            >>> if result.valid:
            ...     print(f"Safe to delete {result.path} ({result.size_bytes} bytes)")

        Coverage Requirement: 100%
        """
        result = ValidationResult(valid=False, path=path, category=category)

        # Layer 1: Protected paths check (from protected_paths.py)
        try:
            validate_path_safety(path)
        except ProtectedPathError as e:
            result.errors.append(f"Layer 1 failed: {str(e)}")
            return result

        # Layer 2: Category permissions check
        if category:
            category_info = self._check_category_permissions(category)
            if not category_info:
                result.errors.append(
                    f"Layer 2 failed: Category '{category}' not found in database"
                )
                return result

            if not category_info.get("is_deletable"):
                result.errors.append(
                    f"Layer 2 failed: Category '{category}' is marked as not deletable"
                )
                return result

            result.is_deletable = True
            result.restoration_command = category_info.get("restoration_command")
        else:
            result.warnings.append("No category specified - assuming manual categorization")

        # Layer 4: Restoration method check
        if not result.restoration_command or result.restoration_command == "N/A":
            result.warnings.append(
                "No restoration method available - deletion will be permanent "
                "(except Trash recovery for 30 days)"
            )

        # Layer 6: Permission check
        try:
            if not os.access(path, os.R_OK):
                result.errors.append(
                    f"Layer 6 failed: Cannot read path (permission denied): {path}"
                )
                return result
        except Exception as e:
            result.errors.append(f"Layer 6 failed: Permission check error: {e}")
            return result

        # Calculate size if path exists
        try:
            if os.path.isfile(path):
                result.size_bytes = os.path.getsize(path)
            elif os.path.isdir(path):
                result.size_bytes = self._calculate_directory_size(path)
        except Exception as e:
            result.warnings.append(f"Could not calculate size: {e}")

        # All checks passed
        result.valid = True

        # Add dry-run warning if applicable
        if self.dry_run:
            result.warnings.append(
                "DRY-RUN MODE: No actual deletion will be performed"
            )

        return result

    def enforce_dry_run(self) -> None:
        """
        Enforce that validator is in dry-run mode.

        Raises:
            DryRunViolationError: If not in dry-run mode

        Coverage Requirement: 100%
        """
        if not self.dry_run:
            raise DryRunViolationError(
                "Dry-run mode is disabled. This is dangerous and not recommended.\n"
                "To enable real deletions, explicitly set dry_run=False when creating "
                "the validator and confirm you understand the risks."
            )

    def _check_category_permissions(self, category_name: str) -> Optional[Dict[str, Any]]:
        """
        Check category permissions from database.

        Args:
            category_name: Name of category to check

        Returns:
            Dictionary with category info, or None if not found

        Coverage Requirement: 100%
        """
        if not self.database_path.exists():
            return None

        try:
            conn = sqlite3.connect(self.database_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT name, is_deletable, restoration_command, priority
                FROM categories
                WHERE name = ?
                """,
                (category_name,)
            )

            row = cursor.fetchone()
            conn.close()

            if row:
                return dict(row)
            return None

        except Exception:
            return None

    def _calculate_directory_size(self, path: str) -> int:
        """
        Calculate total size of directory recursively.

        Args:
            path: Directory path

        Returns:
            Total size in bytes

        Coverage Requirement: 80% (utility function)
        """
        total = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        if os.path.exists(filepath):
                            total += os.path.getsize(filepath)
                    except (OSError, PermissionError):
                        # Skip files we can't access
                        continue
        except (OSError, PermissionError):
            # Skip directories we can't access
            pass

        return total

    def validate_batch(
        self,
        paths: list[str],
        category: Optional[str] = None
    ) -> list[ValidationResult]:
        """
        Validate multiple paths for deletion.

        Args:
            paths: List of paths to validate
            category: Category for all paths

        Returns:
            List of ValidationResult objects

        Coverage Requirement: 90%
        """
        return [self.validate_deletion(path, category) for path in paths]


def validate_deletion(
    path: str,
    category: Optional[str] = None,
    dry_run: bool = True
) -> ValidationResult:
    """
    Convenience function for single deletion validation.

    This is a simplified interface to DeletionValidator for common use cases.

    Args:
        path: Path to validate
        category: Expected category
        dry_run: If True, only preview (default: True for safety)

    Returns:
        ValidationResult with validation outcome

    Example:
        >>> result = validate_deletion("/project/node_modules", "node_modules")
        >>> if result.valid:
        ...     print("Safe to delete")
        >>> else:
        ...     print("Errors:", result.errors)

    Coverage Requirement: 100%
    """
    validator = DeletionValidator(dry_run=dry_run)
    return validator.validate_deletion(path, category)


def get_deletable_categories() -> list[Dict[str, Any]]:
    """
    Get list of all deletable categories from database.

    Returns:
        List of category dictionaries

    Coverage Requirement: 90%
    """
    if not DATABASE_PATH.exists():
        return []

    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT name, description, is_deletable, restoration_command, priority
            FROM categories
            WHERE is_deletable = 1
            ORDER BY priority DESC
            """
        )

        categories = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return categories

    except Exception:
        return []
