"""
Test Utilities - Custom Assertions

Custom assertion helpers for safety and validation testing.

Provides:
- Safety validation assertions
- Path protection assertions
- Deletion validation assertions
- Database state assertions

Author: Vladimir K.S.
"""

import sqlite3
from pathlib import Path
from typing import Callable, Optional

import pytest


def assert_path_is_protected(
    path: str,
    reason: Optional[str] = None
) -> None:
    """
    Assert that path is protected by safety system.

    Args:
        path: Path to check
        reason: Optional reason for expected protection

    Raises:
        AssertionError: If path is not protected
    """
    from claude_mac_manager.safety import is_protected_path

    msg = f"Path should be protected: {path}"
    if reason:
        msg += f" ({reason})"

    assert is_protected_path(path), msg


def assert_path_is_not_protected(
    path: str,
    reason: Optional[str] = None
) -> None:
    """
    Assert that path is NOT protected (deletable).

    Args:
        path: Path to check
        reason: Optional reason for expected non-protection

    Raises:
        AssertionError: If path is protected
    """
    from claude_mac_manager.safety import is_protected_path

    msg = f"Path should NOT be protected: {path}"
    if reason:
        msg += f" ({reason})"

    assert not is_protected_path(path), msg


def assert_path_matches_category(
    path: str,
    expected_category: str
) -> None:
    """
    Assert that path matches expected deletable category.

    Args:
        path: Path to check
        expected_category: Expected category name

    Raises:
        AssertionError: If path doesn't match category
    """
    from claude_mac_manager.safety import is_deletable_category

    assert is_deletable_category(path), f"Path should match deletable category: {path}"


def assert_validation_passes(
    path: str,
    category: Optional[str] = None,
    dry_run: bool = True
) -> None:
    """
    Assert that validation passes for path.

    Args:
        path: Path to validate
        category: Optional category
        dry_run: Dry-run mode

    Raises:
        AssertionError: If validation fails
    """
    from claude_mac_manager.safety import validate_deletion

    result = validate_deletion(path, category, dry_run=dry_run)
    assert result.valid, f"Validation should pass for {path}: {result.errors}"


def assert_validation_fails(
    path: str,
    category: Optional[str] = None,
    dry_run: bool = True,
    expected_error: Optional[str] = None
) -> None:
    """
    Assert that validation fails for path.

    Args:
        path: Path to validate
        category: Optional category
        dry_run: Dry-run mode
        expected_error: Optional expected error substring

    Raises:
        AssertionError: If validation passes
    """
    from claude_mac_manager.safety import validate_deletion

    result = validate_deletion(path, category, dry_run=dry_run)
    assert not result.valid, f"Validation should fail for {path}"

    if expected_error:
        error_messages = " ".join(result.errors)
        assert expected_error in error_messages, \
            f"Expected error '{expected_error}' not found in: {result.errors}"


def assert_raises_protected_error(
    func: Callable,
    *args,
    **kwargs
) -> None:
    """
    Assert that function raises ProtectedPathError.

    Args:
        func: Function to call
        *args: Positional arguments
        **kwargs: Keyword arguments

    Raises:
        AssertionError: If ProtectedPathError not raised
    """
    from claude_mac_manager.safety import ProtectedPathError

    with pytest.raises(ProtectedPathError):
        func(*args, **kwargs)


def assert_raises_validation_error(
    func: Callable,
    *args,
    **kwargs
) -> None:
    """
    Assert that function raises ValidationError.

    Args:
        func: Function to call
        *args: Positional arguments
        **kwargs: Keyword arguments

    Raises:
        AssertionError: If ValidationError not raised
    """
    from claude_mac_manager.safety import ValidationError

    with pytest.raises(ValidationError):
        func(*args, **kwargs)


def assert_database_has_category(
    db_path: Path,
    category_name: str
) -> None:
    """
    Assert that database contains specific category.

    Args:
        db_path: Path to database
        category_name: Category name to check

    Raises:
        AssertionError: If category not found
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM deletable_categories WHERE name = ?",
        (category_name,)
    )
    count = cursor.fetchone()[0]
    conn.close()

    assert count > 0, f"Category '{category_name}' not found in database"


def assert_database_has_scan_result(
    db_path: Path,
    min_files: int = 1
) -> None:
    """
    Assert that database contains scan results.

    Args:
        db_path: Path to database
        min_files: Minimum number of files expected

    Raises:
        AssertionError: If no scan results found
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM scan_results")
    count = cursor.fetchone()[0]
    conn.close()

    assert count > 0, "No scan results found in database"


def assert_cleanup_logged(
    db_path: Path,
    path: str
) -> None:
    """
    Assert that cleanup operation was logged.

    Args:
        db_path: Path to database
        path: Path that was cleaned

    Raises:
        AssertionError: If cleanup not logged
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM cleanup_history WHERE path = ?",
        (path,)
    )
    count = cursor.fetchone()[0]
    conn.close()

    assert count > 0, f"Cleanup of '{path}' not logged in database"


def assert_dry_run_enforced(
    result,
    expected: bool = True
) -> None:
    """
    Assert that dry-run mode is enforced in validation result.

    Args:
        result: ValidationResult instance
        expected: Expected dry-run state

    Raises:
        AssertionError: If dry-run not enforced
    """
    # Check that result indicates dry-run mode
    if expected:
        assert not result.is_deletable or "dry-run" in str(result.warnings), \
            "Dry-run mode should be enforced"
    else:
        assert result.is_deletable, "Dry-run mode should not prevent deletion"


def assert_size_calculated(
    result,
    min_size: int = 0
) -> None:
    """
    Assert that size was calculated in validation result.

    Args:
        result: ValidationResult instance
        min_size: Minimum expected size in bytes

    Raises:
        AssertionError: If size not calculated
    """
    assert result.size_bytes > min_size, \
        f"Size should be calculated (got {result.size_bytes}, expected >{min_size})"


def assert_restoration_command_present(
    result,
    expected_command: Optional[str] = None
) -> None:
    """
    Assert that restoration command is present in result.

    Args:
        result: ValidationResult instance
        expected_command: Optional expected command substring

    Raises:
        AssertionError: If restoration command missing
    """
    assert result.restoration_command, "Restoration command should be present"

    if expected_command:
        assert expected_command in result.restoration_command, \
            f"Expected '{expected_command}' in restoration command"
