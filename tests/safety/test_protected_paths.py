"""
Tests for Protected Paths Module (Layer 1 Safety)

CRITICAL: This module requires 100% test coverage.

Tests for:
- is_protected_path() - core safety function
- is_deletable_category() - allowlist validation
- validate_path_safety() - combined checks
- _normalize_path() - path expansion
- Edge cases: symlinks, relative paths, ~/ expansion

Author: Vladimir K.S.
"""

import pytest
from pathlib import Path

# TODO: Implement tests for protected_paths.py
# Coverage target: 100% (safety-critical)
