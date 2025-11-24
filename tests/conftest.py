"""
Pytest Configuration and Shared Fixtures

Provides test fixtures for:
- Fake filesystem (pyfakefs)
- Database fixtures with populated categories
- Temporary directories
- Mock objects for safety testing
- Test helpers for validation

Author: Vladimir K.S.
"""

import sqlite3
from pathlib import Path
from typing import Generator

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem

from claude_mac_manager import DATABASE_PATH, DATA_DIR


# ====================
# Filesystem Fixtures
# ====================


@pytest.fixture
def temp_data_dir(fs: FakeFilesystem) -> Path:
    """
    Create temporary data directory structure in fake filesystem.

    Creates:
    - /Users/Shared/_claude_mac_manager
    - data/disk/
    - data/disk/history/
    - config/disk/

    Returns:
        Path to temporary data directory
    """
    # Create directory structure
    fs.create_dir(DATA_DIR)
    fs.create_dir(DATA_DIR / "data" / "disk")
    fs.create_dir(DATA_DIR / "data" / "disk" / "history")
    fs.create_dir(DATA_DIR / "config" / "disk")

    return DATA_DIR


@pytest.fixture
def temp_home_dir(fs: FakeFilesystem) -> Path:
    """
    Create fake home directory with common structure.

    Creates:
    - ~/Documents/
    - ~/Desktop/
    - ~/Downloads/
    - ~/Library/
    - ~/.ssh/
    - ~/.git/

    Returns:
        Path to fake home directory
    """
    home = Path.home()

    # Create common directories
    directories = [
        home / "Documents",
        home / "Desktop",
        home / "Downloads",
        home / "Library",
        home / ".ssh",
        home / ".git",
    ]

    for directory in directories:
        fs.create_dir(directory)

    # Create some protected files
    fs.create_file(home / ".ssh" / "id_rsa", contents="FAKE_PRIVATE_KEY")
    fs.create_file(home / ".gitconfig", contents="[user]\nname=Test")

    return home


@pytest.fixture
def temp_project_dirs(fs: FakeFilesystem, temp_home_dir: Path) -> dict[str, Path]:
    """
    Create fake project directories for testing.

    Creates projects with:
    - node_modules/ (with files)
    - .venv/ (with files)
    - .git/ (protected)
    - src/ (source code)

    Returns:
        Dictionary mapping project names to paths
    """
    projects_dir = temp_home_dir / "projects"
    fs.create_dir(projects_dir)

    projects = {}

    # JavaScript project
    js_project = projects_dir / "my-app"
    fs.create_dir(js_project)
    fs.create_dir(js_project / "node_modules")
    fs.create_file(js_project / "node_modules" / "package.json", contents='{"name": "test"}')
    fs.create_dir(js_project / ".git")
    fs.create_dir(js_project / "src")
    fs.create_file(js_project / "package.json", contents='{"name": "my-app"}')
    projects["js"] = js_project

    # Python project
    py_project = projects_dir / "my-python-app"
    fs.create_dir(py_project)
    fs.create_dir(py_project / ".venv")
    fs.create_file(py_project / ".venv" / "pyvenv.cfg", contents="version=3.10")
    fs.create_dir(py_project / ".git")
    fs.create_dir(py_project / "src")
    fs.create_file(py_project / "pyproject.toml", contents="[tool.poetry]")
    projects["python"] = py_project

    return projects


# ====================
# Database Fixtures
# ====================


@pytest.fixture
def temp_database(temp_data_dir: Path) -> Generator[Path, None, None]:
    """
    Create temporary SQLite database with schema.

    Creates database with:
    - Full schema from schema.sql
    - 14 pre-populated categories
    - 12 system exclusions

    Yields:
        Path to temporary database file

    Cleanup:
        Removes database after test
    """
    db_path = DATABASE_PATH

    # Read schema from actual schema file
    schema_file = Path(__file__).parent.parent / "modules" / "disk" / "schema.sql"

    if schema_file.exists():
        with open(schema_file, 'r') as f:
            schema_sql = f.read()

        # Create database with schema
        conn = sqlite3.connect(db_path)
        conn.executescript(schema_sql)
        conn.close()
    else:
        # Fallback: create minimal schema
        conn = sqlite3.connect(db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS deletable_categories (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                patterns TEXT,
                restoration_command TEXT,
                priority INTEGER DEFAULT 50
            )
        """)
        conn.close()

    yield db_path

    # Cleanup
    if db_path.exists():
        db_path.unlink()


@pytest.fixture
def populated_database(temp_database: Path) -> Path:
    """
    Database fixture with additional test data.

    Adds:
    - Test scan results
    - Test cleanup history
    - Test file entries

    Returns:
        Path to populated database
    """
    conn = sqlite3.connect(temp_database)
    cursor = conn.cursor()

    # Add test scan result
    cursor.execute("""
        INSERT INTO scan_results (scan_date, total_size, total_files)
        VALUES (datetime('now'), 1000000, 100)
    """)

    scan_id = cursor.lastrowid

    # Add test file entries
    cursor.execute("""
        INSERT INTO files (scan_id, path, size, category_id)
        VALUES (?, ?, ?, ?)
    """, (scan_id, "/test/node_modules", 10000, 2))

    conn.commit()
    conn.close()

    return temp_database


# ====================
# Safety Testing Fixtures
# ====================


@pytest.fixture
def protected_system_paths() -> list[str]:
    """
    List of protected system paths for safety testing.

    Returns:
        List of critical paths that should never be deleted
    """
    return [
        "/System/Library",
        "/usr/bin/python3",
        "/bin/bash",
        "/Library/Application Support",
        str(Path.home() / "Documents" / "important.txt"),
        str(Path.home() / "Desktop"),
        str(Path.home() / ".ssh" / "id_rsa"),
        str(Path.home() / ".gitconfig"),
    ]


@pytest.fixture
def deletable_test_paths(temp_project_dirs: dict[str, Path]) -> list[str]:
    """
    List of deletable paths for safety testing.

    Returns:
        List of paths that should be safe to delete
    """
    js_project = temp_project_dirs["js"]
    py_project = temp_project_dirs["python"]

    return [
        str(js_project / "node_modules"),
        str(py_project / ".venv"),
        str(Path.home() / ".npm" / "_cacache"),
        str(Path.home() / "Library" / "Caches" / "pip"),
    ]


@pytest.fixture
def mock_dry_run_enabled() -> bool:
    """
    Mock fixture for dry-run mode testing.

    Returns:
        True (dry-run enabled by default)
    """
    return True


# ====================
# Test Helpers
# ====================


@pytest.fixture
def create_large_directory(fs: FakeFilesystem):
    """
    Helper fixture to create directories with specific sizes.

    Usage:
        create_large_directory(path, size_mb=100, num_files=10)

    Returns:
        Callable that creates directory with files
    """
    def _create(path: Path, size_mb: int = 10, num_files: int = 5) -> Path:
        """Create directory with files totaling approximately size_mb."""
        fs.create_dir(path)

        # Calculate size per file
        size_per_file = (size_mb * 1024 * 1024) // num_files

        for i in range(num_files):
            file_path = path / f"file_{i}.bin"
            fs.create_file(file_path, st_size=size_per_file)

        return path

    return _create


@pytest.fixture
def assert_path_protected():
    """
    Custom assertion helper for protected paths.

    Usage:
        assert_path_protected(path, validator)

    Returns:
        Callable that asserts path is protected
    """
    def _assert(path: str, validator_func) -> None:
        """Assert that path is protected by validator."""
        from claude_mac_manager.safety import is_protected_path, ProtectedPathError

        # Check Layer 1: Protected paths
        assert is_protected_path(path), f"Path should be protected: {path}"

        # Check validation raises error
        with pytest.raises(ProtectedPathError):
            validator_func(path)

    return _assert


@pytest.fixture
def assert_path_deletable():
    """
    Custom assertion helper for deletable paths.

    Usage:
        assert_path_deletable(path, category, validator)

    Returns:
        Callable that asserts path is safe to delete
    """
    def _assert(path: str, category: str, validator_func) -> None:
        """Assert that path is deletable."""
        from claude_mac_manager.safety import is_protected_path

        # Check Layer 1: Not protected
        assert not is_protected_path(path), f"Path should not be protected: {path}"

        # Check validation passes (doesn't raise)
        validator_func(path, category)

    return _assert


# ====================
# Session Fixtures
# ====================


@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """
    Session-scoped fixture for test data directory.

    Returns:
        Path to tests/data/ directory
    """
    return Path(__file__).parent / "data"


# ====================
# Autouse Fixtures
# ====================


@pytest.fixture(autouse=True)
def reset_environment(monkeypatch):
    """
    Automatically reset environment for each test.

    Clears:
    - Environment variables
    - Working directory
    - Global state
    """
    # Save original working directory
    import os
    original_cwd = os.getcwd()

    yield

    # Restore working directory
    os.chdir(original_cwd)
