# Claude Mac Manager

**Author:** Vladimir K.S.
**Created:** 2025-11-24
**Purpose:** Comprehensive macOS system management toolkit

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

## Contributing

This is a personal system management toolkit. Future enhancements will be driven by actual needs and usage patterns.

**Development Principles:**
- Safety first (never delete without confirmation)
- Efficiency (parallel operations, caching)
- Transparency (all operations logged and reversible)
- Accessibility (clear documentation for non-technical use)
