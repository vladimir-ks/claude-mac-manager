# Claude Mac Manager

[![Tests](https://github.com/vladimir-ks/claude-mac-manager/workflows/Tests/badge.svg)](https://github.com/vladimir-ks/claude-mac-manager/actions/workflows/test.yml)
[![Lint](https://github.com/vladimir-ks/claude-mac-manager/workflows/Lint/badge.svg)](https://github.com/vladimir-ks/claude-mac-manager/actions/workflows/lint.yml)
[![codecov](https://codecov.io/gh/vladimir-ks/claude-mac-manager/branch/master/graph/badge.svg)](https://codecov.io/gh/vladimir-ks/claude-mac-manager)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Author:** Vladimir K.S.
**Version:** 0.0.1 (Pre-Alpha)
**Created:** 2025-11-24
**Purpose:** Comprehensive macOS system management toolkit

> ⚠️ **Development Status:** This project is in early development (v0.0.1). Core functionality is being implemented. Not ready for production use.

---

## Vision

A centralized system for managing your Mac through Claude Code. Starting with disk space management, expandable to full system automation including Homebrew, security audits, performance monitoring, and backups.

---

## Project Structure

```
/_claude_mac_manager/
├── modules/          # Feature modules
│   ├── disk/        # Disk space management (ACTIVE)
│   ├── brew/        # Homebrew management (PLANNED)
│   ├── security/    # Security audits (PLANNED)
│   ├── performance/ # Performance monitoring (PLANNED)
│   └── backups/     # Backup management (PLANNED)
├── data/            # Persistent data storage
│   ├── disk/        # Disk analysis data
│   │   ├── cache.db # SQLite database with scan results
│   │   ├── current.json  # Latest scan export
│   │   └── history/ # Historical scans (timestamped)
│   └── system/      # System-wide data
│       └── baseline.yaml  # System state snapshot
├── config/          # Configuration files
│   ├── disk/        # Disk module config
│   │   ├── exclusions.yaml  # Directories to skip
│   │   ├── categories.yaml  # Classification rules
│   │   └── profiles.yaml    # Scan profiles
│   └── global.yaml  # System-wide settings
├── agents/          # Claude Code specialized agents
│   └── disk-scanner/  # Parallel scanning agents
├── scripts/         # Utility scripts
│   ├── cleanup_dependencies.sh  # Original cleanup script
│   └── utils/       # Helper utilities
└── docs/            # Documentation
    ├── README.md              # This file
    ├── disk-management.md     # Disk module documentation
    └── architecture.md        # System architecture
```

---

## Current Status: Phase 1 - Disk Management

### Features

**Scanning:**
- System-wide disk analysis from root (/)
- Parallel scanning (8 threads)
- Merkle tree-based change detection
- Incremental updates (only rescan changed areas)

**Storage:**
- SQLite database for fast queries (<4ms)
- JSON exports for version control
- Historical tracking

**Analysis:**
- Automatic categorization (node_modules, venvs, caches, logs)
- Size trends over time
- Cleanup recommendations
- Duplicate detection

**Cleanup:**
- Safe deletion (moves to Trash, not rm -rf)
- Dry-run previews
- Protected directory list
- Rollback support

### Usage

**Initial Scan:**
```bash
cd /Users/Shared/_claude_mac_manager
# Run scanner (implementation pending)
```

**Quick Status:**
```bash
# View current disk usage summary
```

**Cleanup:**
```bash
# Interactive cleanup with previews
```

---

## Safety Features

1. **Read-Only Scanning** - Analysis never modifies files
2. **Protected Directories** - System files are never targeted
3. **Trash-Based Deletion** - 30-day recovery window
4. **Dry-Run Mode** - Preview all changes before applying
5. **Permission Handling** - Gracefully handles restricted areas

---

## Location Note

**Actual Path:** `/Users/Shared/_claude_mac_manager`
**Symlink:** `~/claude_mac_manager` (for convenience)

Located in `/Users/Shared/` because:
- Standard macOS location for shared resources
- Writable without sudo
- Accessible to all users (single-user Mac)
- Not subject to System Integrity Protection

---

## Future Modules

### Phase 2: Homebrew Management
- Track installed packages
- Audit for outdated/unused dependencies
- Dependency tree analysis

### Phase 3: Security Auditing
- Permission scanning
- Vulnerable software detection
- Certificate management

### Phase 4: Performance Monitoring
- Process analysis
- Startup optimization
- Resource usage tracking

### Phase 5: Backup Management
- Time Machine status
- Cloud backup verification
- Selective backup configurations

---

## Technical Details

**Language:** Python + SQL + Bash
**Database:** SQLite3
**Version Control:** Git
**Claude Code Integration:** Specialized agents for parallel operations

---

## Recent Cleanup (2025-11-24)

Successfully freed **4.66 GB** through dependency cleanup:
- NPM cache: 1.4 GB
- Gemini history: 360 MB
- node_modules (4 projects): 2.03 GB
- Python venvs (2 projects): 868 MB
- Archived projects: 88 MB

All dependencies safely removed with restoration paths documented.

---

## Development Setup

### Prerequisites
- macOS 13+ (Ventura or later)
- Python 3.10+
- Poetry 1.7.1+
- Git

### Quick Start

```bash
# Clone repository
git clone https://github.com/vladimir-ks/claude-mac-manager.git
cd claude-mac-manager

# Install dependencies
poetry install

# Install pre-commit hooks
poetry run pre-commit install

# Run tests
poetry run pytest

# Run CLI
poetry run cmm --version
poetry run cmm status
```

### Development Commands

```bash
# Format code
poetry run black .

# Lint code
poetry run ruff check .

# Type check
poetry run mypy claude_mac_manager/

# Run tests with coverage
poetry run pytest --cov

# Run safety-critical tests only
poetry run pytest tests/safety/ -m safety

# Install as editable package
poetry install

# Build package
poetry build
```

### Testing Philosophy

- **Spec-Driven:** All features start with specifications
- **Test-First:** Tests before implementation when possible
- **100% Safety Coverage:** Safety-critical modules require perfect coverage
- **85% Overall:** Minimum coverage for all code
- **pyfakefs:** Fake filesystem for safe testing

### Project Structure

```
claude_mac_manager/
├── cli.py              # CLI interface
├── install.py          # Post-install automation
├── safety/             # Multi-layer safety system
│   ├── protected_paths.py  # Layer 1: Path protection
│   └── validator.py        # Layers 2-6: Validation
├── scanner/            # Filesystem scanning (pending)
├── analyzer/           # Analysis engine (pending)
└── database/           # Database operations (pending)

tests/
├── conftest.py         # Shared fixtures
├── safety/             # Safety tests (100% coverage required)
├── unit/               # Unit tests
├── integration/        # Integration tests
└── utils/              # Test utilities
```

---

## Contributing

This is a personal system management toolkit. Future enhancements will be driven by actual needs and usage patterns.

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed development guidelines.

**Development Principles:**
- Safety first (never delete without confirmation)
- Efficiency (parallel operations, caching)
- Transparency (all operations logged and reversible)
- Accessibility (clear documentation for non-technical use)
