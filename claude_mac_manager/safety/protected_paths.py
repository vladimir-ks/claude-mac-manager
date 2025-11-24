"""
Protected Paths - Layer 1 Safety System

Defines and enforces protection for critical macOS system paths and user data.
These paths should NEVER be deleted by any cleanup operation.

Author: Vladimir K.S.
Coverage Requirement: 100% (safety-critical)
"""

import os
from pathlib import Path
from typing import List
import pathspec


class ProtectedPathError(Exception):
    """Raised when attempting to access or delete a protected path."""
    pass


# ====================
# PROTECTED PATHS (Whitelist - NEVER DELETE)
# ====================

PROTECTED_PATHS: List[str] = [
    # macOS System Directories
    "/System/**",           # macOS system files (SIP protected)
    "/bin/**",              # System binaries
    "/sbin/**",             # System admin binaries
    "/usr/bin/**",          # Unix binaries
    "/usr/sbin/**",         # Unix admin binaries
    "/usr/lib/**",          # System libraries
    "/private/var/vm/**",   # Virtual memory swap

    # User Data (CRITICAL - Never delete)
    "~/Documents/**",       # User documents
    "~/Desktop/**",         # Desktop files
    "~/Downloads/**",       # Downloads
    "~/Pictures/**",        # Photos
    "~/Movies/**",          # Videos
    "~/Music/**",           # Music library

    # Development Critical
    "**/.git/**",           # Git repositories
    "**/.github/**",        # GitHub configurations
    "**/.gitlab/**",        # GitLab configurations
    "**/LICENSE",           # License files
    "**/README.md",         # Documentation

    # Applications
    "/Applications/**",     # Installed applications (require manual approval)
    "~/Library/Application Support/**",  # App data

    # System Configuration
    "/etc/**",              # System configuration
    "/Library/**",          # System library
    "~/.ssh/**",            # SSH keys (CRITICAL)
    "~/.gnupg/**",          # GPG keys (CRITICAL)
    "~/.aws/**",            # AWS credentials (CRITICAL)
    "~/.config/**",         # User configuration

    # Database & Important Data
    "**/data/**",           # Generic data directories
    "**/database/**",       # Database directories
    "**/db/**",             # Database directories
    "**/backup/**",         # Backup directories
    "**/backups/**",        # Backup directories

    # Claude Mac Manager Self-Protection
    "/Users/Shared/_claude_mac_manager/data/**",      # Our database
    "/Users/Shared/_claude_mac_manager/config/**",    # Our config
    "/Users/Shared/_claude_mac_manager/CLAUDE.md",    # Project context
    "/Users/Shared/_claude_mac_manager/README.md",    # Documentation
]


# ====================
# DELETABLE CATEGORIES (Explicit Allow-list)
# ====================

DELETABLE_PATTERNS: List[str] = [
    # Node.js
    "**/node_modules/**",   # Can restore with: npm install
    "~/.npm/_npx/**",       # NPM cache (auto-regenerated)
    "~/.npm/_cacache/**",   # NPM cache

    # Python
    "**/.venv/**",          # Virtual environments (restorable)
    "**/venv/**",           # Virtual environments
    "**/env/**",            # Virtual environments
    "**/__pycache__/**",    # Python bytecode (auto-regenerated)
    "**/*.pyc",             # Python bytecode
    "**/*.pyo",             # Python bytecode optimized
    "**/.pytest_cache/**",  # Pytest cache
    "**/.mypy_cache/**",    # MyPy cache
    "**/.ruff_cache/**",    # Ruff cache

    # Ruby
    "**/vendor/bundle/**",  # Bundler gems (restorable)
    "~/.gem/cache/**",      # Gem cache

    # Rust
    "**/target/debug/**",   # Rust debug builds (restorable)
    "**/target/release/**", # Rust release builds

    # Go
    "~/.cache/go-build/**", # Go build cache
    "**/pkg/mod/**",        # Go modules cache

    # JavaScript/TypeScript Build Artifacts
    "**/dist/**",           # Build output
    "**/build/**",          # Build output
    "**/.next/**",          # Next.js cache
    "**/.nuxt/**",          # Nuxt.js cache

    # macOS System
    "**/.DS_Store",         # macOS metadata (auto-regenerated)
    "**/.localized",        # Localization metadata

    # Logs
    "**/*.log",             # Log files
    "**/logs/**",           # Log directories
    "**/_logs/**",          # Log directories

    # Temporary Files
    "**/tmp/**",            # Temporary directories
    "**/temp/**",           # Temporary directories
    "**/.tmp/**",           # Hidden temporary
    "**/cache/**",          # Cache directories
    "**/.cache/**",         # Hidden cache

    # IDE/Editor
    "**/.vscode/cache/**",  # VSCode cache
    "**/.idea/cache/**",    # IntelliJ cache
]


def _normalize_path(path: str) -> Path:
    """
    Normalize path by expanding user home and resolving symlinks.

    Args:
        path: Path to normalize (can include ~ or relative paths)

    Returns:
        Normalized absolute Path object

    Example:
        >>> _normalize_path("~/Documents")
        PosixPath('/Users/vmks/Documents')
    """
    return Path(os.path.expanduser(path)).resolve()


def is_protected_path(path: str) -> bool:
    """
    Check if path matches any protected pattern.

    This is Layer 1 of the safety system. Protected paths can NEVER
    be deleted by any operation, regardless of category or user confirmation.

    Args:
        path: Path to check (can be relative, absolute, or use ~)

    Returns:
        True if path is protected, False if safe to consider for deletion

    Raises:
        No exceptions raised - returns False on any error for safety

    Example:
        >>> is_protected_path("/System/Library")
        True
        >>> is_protected_path("/Users/vmks/project/node_modules")
        False

    Coverage Requirement: 100%
    """
    try:
        normalized = _normalize_path(path)
        normalized_str = str(normalized)

        # Create pathspec matcher for protected patterns
        spec = pathspec.PathSpec.from_lines('gitwildmatch', PROTECTED_PATHS)

        # Check if path matches any protected pattern
        if spec.match_file(normalized_str):
            return True

        # Additional check: ensure we're not under any protected parent
        for protected_pattern in PROTECTED_PATHS:
            # Expand wildcards for parent check
            if '**' in protected_pattern:
                base = protected_pattern.replace('/**', '')
                base = os.path.expanduser(base)
                if normalized_str.startswith(base):
                    return True

        return False

    except Exception:
        # On any error, assume protected for safety
        return True


def is_deletable_category(path: str) -> bool:
    """
    Check if path matches any explicitly deletable pattern.

    This is used in conjunction with is_protected_path(). A path must:
    1. NOT be protected (is_protected_path() == False)
    2. AND match a deletable category (this function returns True)

    Args:
        path: Path to check

    Returns:
        True if path matches deletable category, False otherwise

    Example:
        >>> is_deletable_category("/Users/vmks/project/node_modules")
        True
        >>> is_deletable_category("/Users/vmks/random_folder")
        False

    Coverage Requirement: 100%
    """
    try:
        normalized = _normalize_path(path)
        normalized_str = str(normalized)

        # Create pathspec matcher for deletable patterns
        spec = pathspec.PathSpec.from_lines('gitwildmatch', DELETABLE_PATTERNS)

        return spec.match_file(normalized_str)

    except Exception:
        # On any error, assume NOT deletable for safety
        return False


def validate_path_safety(path: str) -> None:
    """
    Validate that path is safe to consider for deletion.

    This function combines both checks:
    1. Path must NOT be protected
    2. Path MUST match a deletable category

    Args:
        path: Path to validate

    Raises:
        ProtectedPathError: If path is protected or doesn't match deletable category

    Example:
        >>> validate_path_safety("/Users/vmks/project/node_modules")
        # No exception - safe

        >>> validate_path_safety("/System/Library")
        ProtectedPathError: Cannot delete protected path: /System/Library

    Coverage Requirement: 100%
    """
    # Check 1: Is path protected?
    if is_protected_path(path):
        raise ProtectedPathError(
            f"Cannot delete protected path: {path}\n"
            f"This path is in the protected paths list and can NEVER be deleted."
        )

    # Check 2: Does path match a deletable category?
    if not is_deletable_category(path):
        raise ProtectedPathError(
            f"Path does not match any deletable category: {path}\n"
            f"Only explicitly allowed categories (node_modules, venv, caches, etc.) can be deleted.\n"
            f"This is a safety measure to prevent accidental deletion of important data."
        )


def get_protected_paths_list() -> List[str]:
    """
    Get list of protected path patterns.

    Returns:
        Copy of PROTECTED_PATHS list

    Coverage Requirement: 100%
    """
    return PROTECTED_PATHS.copy()


def get_deletable_patterns_list() -> List[str]:
    """
    Get list of deletable path patterns.

    Returns:
        Copy of DELETABLE_PATTERNS list

    Coverage Requirement: 100%
    """
    return DELETABLE_PATTERNS.copy()
