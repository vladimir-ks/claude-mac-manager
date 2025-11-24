"""
Test Utilities - Fake Filesystem Helpers

Helper functions for creating fake filesystem structures for testing.

Provides:
- Directory structure creators
- File content generators
- Size calculation helpers
- Path manipulation utilities

Author: Vladimir K.S.
"""

from pathlib import Path
from typing import Optional

from pyfakefs.fake_filesystem import FakeFilesystem


def create_node_modules(
    fs: FakeFilesystem,
    project_path: Path,
    size_mb: int = 50,
    num_packages: int = 100
) -> Path:
    """
    Create fake node_modules directory with packages.

    Args:
        fs: Fake filesystem instance
        project_path: Project root path
        size_mb: Total size in MB
        num_packages: Number of packages to create

    Returns:
        Path to created node_modules directory
    """
    node_modules = project_path / "node_modules"
    fs.create_dir(node_modules)

    # Calculate size per package
    size_per_package = (size_mb * 1024 * 1024) // num_packages

    for i in range(num_packages):
        package_dir = node_modules / f"package-{i}"
        fs.create_dir(package_dir)
        fs.create_file(
            package_dir / "index.js",
            st_size=size_per_package // 2
        )
        fs.create_file(
            package_dir / "package.json",
            contents=f'{{"name": "package-{i}"}}'
        )

    return node_modules


def create_python_venv(
    fs: FakeFilesystem,
    project_path: Path,
    size_mb: int = 30,
    python_version: str = "3.10"
) -> Path:
    """
    Create fake Python virtual environment.

    Args:
        fs: Fake filesystem instance
        project_path: Project root path
        size_mb: Total size in MB
        python_version: Python version string

    Returns:
        Path to created .venv directory
    """
    venv = project_path / ".venv"
    fs.create_dir(venv / "lib" / f"python{python_version}" / "site-packages")
    fs.create_dir(venv / "bin")

    # Create pyvenv.cfg
    fs.create_file(
        venv / "pyvenv.cfg",
        contents=f"version = {python_version}\n"
    )

    # Create fake packages
    site_packages = venv / "lib" / f"python{python_version}" / "site-packages"
    num_packages = 20
    size_per_package = (size_mb * 1024 * 1024) // num_packages

    for i in range(num_packages):
        package_dir = site_packages / f"package_{i}"
        fs.create_dir(package_dir)
        fs.create_file(
            package_dir / "__init__.py",
            st_size=size_per_package
        )

    return venv


def create_git_repo(
    fs: FakeFilesystem,
    project_path: Path,
    with_history: bool = True
) -> Path:
    """
    Create fake .git repository directory.

    Args:
        fs: Fake filesystem instance
        project_path: Project root path
        with_history: Whether to create fake git objects

    Returns:
        Path to created .git directory
    """
    git_dir = project_path / ".git"
    fs.create_dir(git_dir / "objects")
    fs.create_dir(git_dir / "refs" / "heads")
    fs.create_dir(git_dir / "refs" / "tags")

    # Create config
    fs.create_file(
        git_dir / "config",
        contents="[core]\nrepositoryformatversion = 0\n"
    )

    # Create HEAD
    fs.create_file(
        git_dir / "HEAD",
        contents="ref: refs/heads/main\n"
    )

    if with_history:
        # Create fake objects
        for i in range(10):
            obj_dir = git_dir / "objects" / f"{i:02x}"
            fs.create_dir(obj_dir)
            fs.create_file(
                obj_dir / f"{'a' * 38}",
                st_size=1024
            )

    return git_dir


def create_cache_directory(
    fs: FakeFilesystem,
    cache_path: Path,
    size_mb: int = 100,
    num_files: int = 50
) -> Path:
    """
    Create fake cache directory with files.

    Args:
        fs: Fake filesystem instance
        cache_path: Cache directory path
        size_mb: Total size in MB
        num_files: Number of cache files

    Returns:
        Path to created cache directory
    """
    fs.create_dir(cache_path)

    size_per_file = (size_mb * 1024 * 1024) // num_files

    for i in range(num_files):
        cache_file = cache_path / f"cache-{i}.bin"
        fs.create_file(cache_file, st_size=size_per_file)

    return cache_path


def create_project_structure(
    fs: FakeFilesystem,
    project_path: Path,
    project_type: str = "node",
    include_dependencies: bool = True,
    include_git: bool = True
) -> Path:
    """
    Create complete project structure.

    Args:
        fs: Fake filesystem instance
        project_path: Project root path
        project_type: Type of project ("node", "python", "rust", "go")
        include_dependencies: Whether to create dependency directories
        include_git: Whether to create .git directory

    Returns:
        Path to created project directory
    """
    fs.create_dir(project_path)

    # Create source directory
    fs.create_dir(project_path / "src")
    fs.create_file(project_path / "src" / "main.py", contents="# Main file")

    # Create README
    fs.create_file(
        project_path / "README.md",
        contents=f"# {project_path.name}\n"
    )

    if include_git:
        create_git_repo(fs, project_path)

    if include_dependencies:
        if project_type == "node":
            create_node_modules(fs, project_path)
            fs.create_file(
                project_path / "package.json",
                contents='{"name": "test-project"}'
            )
        elif project_type == "python":
            create_python_venv(fs, project_path)
            fs.create_file(
                project_path / "pyproject.toml",
                contents="[tool.poetry]\nname = 'test-project'\n"
            )

    return project_path


def calculate_directory_size(fs: FakeFilesystem, path: Path) -> int:
    """
    Calculate total size of directory in fake filesystem.

    Args:
        fs: Fake filesystem instance
        path: Directory path

    Returns:
        Total size in bytes
    """
    total_size = 0

    if not path.exists():
        return 0

    for item in path.rglob("*"):
        if item.is_file():
            total_size += item.stat().st_size

    return total_size


def create_protected_structure(fs: FakeFilesystem, home: Path) -> dict[str, Path]:
    """
    Create structure with protected directories and files.

    Args:
        fs: Fake filesystem instance
        home: Home directory path

    Returns:
        Dictionary mapping protection type to paths
    """
    protected = {}

    # Documents
    documents = home / "Documents"
    fs.create_dir(documents)
    fs.create_file(documents / "important.txt", contents="Important data")
    protected["documents"] = documents

    # Desktop
    desktop = home / "Desktop"
    fs.create_dir(desktop)
    fs.create_file(desktop / "notes.txt", contents="Desktop notes")
    protected["desktop"] = desktop

    # SSH keys
    ssh = home / ".ssh"
    fs.create_dir(ssh)
    fs.create_file(ssh / "id_rsa", contents="PRIVATE KEY")
    fs.create_file(ssh / "id_rsa.pub", contents="PUBLIC KEY")
    protected["ssh"] = ssh

    # Git config
    fs.create_file(home / ".gitconfig", contents="[user]\nname=Test")
    protected["gitconfig"] = home / ".gitconfig"

    return protected
