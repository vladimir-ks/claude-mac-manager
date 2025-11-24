# Claude Mac Manager - Project Context

**Author:** Vladimir K.S.
**Purpose:** Comprehensive macOS system management toolkit
**Location:** `/Users/Shared/_claude_mac_manager`
**Current Phase:** Foundation complete, scanner implementation next

---

## Project Overview

Claude Mac Manager is a comprehensive system management toolkit for macOS, starting with disk space analysis and cleanup, expandable to Homebrew management, security auditing, performance monitoring, and backup management.

**Key Characteristics:**
- **Owner:** Non-technical Product Owner (Business Analyst background)
- **Workflow:** SDD → BDD → TDD (specifications must be approved before implementation)
- **Safety-Critical:** System management tool requiring extreme caution
- **Single-User Mac:** All features optimized for personal use

---

## Core Principles (Inherited from Global ~/.claude/CLAUDE.md)

### Documentation Standards
- **NO CODE SNIPPETS** in documentation (use pseudocode, Mermaid diagrams, or plain English)
- **Exceptions:** JSON, YAML, SQL for data structures only
- **Audience:** All documentation must be accessible to non-technical stakeholders
- **Clarity:** Spartan tone - maximum clarity with minimum words

### Development Workflow
1. **Specification-Driven Development (SDD)**
   - Never write code without approved specifications
   - All specs must be code-free and conceptual
   - Document in `docs/specs/`

2. **Behavior-Driven Development (BDD)**
   - Use Gherkin `.feature` files to explain system behavior
   - Define scenarios BEFORE writing code
   - Document in `docs/features/`

3. **Test-Driven Development (TDD)**
   - Write tests first when possible
   - All code must be verifiable
   - Specs and BDD always precede code and tests

---

## Project-Specific Safety Rules

### CRITICAL - System Management Safety

**File Deletion Protocol:**
1. ❌ **NEVER** use `rm -rf` directly
2. ✅ **ALWAYS** move to Trash (`~/.Trash/`) for 30-day recovery
3. ✅ **REQUIRE** explicit user confirmation for all deletions
4. ✅ **DEFAULT** to dry-run mode (preview only)
5. ✅ **LOG** every operation to `cleanup_history` table

**Protected Paths (NEVER Target):**
- `/System/**` - macOS system files
- `/bin/**`, `/sbin/**` - System binaries
- `/usr/**` (except `/usr/local/`) - Unix system resources
- `/private/var/vm/**` - Virtual memory
- `**/.git/**` - Git repositories
- `~/Documents/**`, `~/Desktop/**`, `~/Downloads/**` - User data
- `/Applications/**` - Installed applications (require manual approval)

**Deletable Paths (Safe with Confirmation):**
- `**/node_modules` - Node.js dependencies (restorable via `npm install`)
- `**/.venv`, `**/venv` - Python virtual environments (restorable via `pip`/`poetry`)
- `~/.npm/_npx/**` - NPM cache (auto-regenerated)
- `**/__pycache__` - Python bytecode (auto-regenerated)
- `**/target` - Rust build artifacts (restorable via `cargo build`)
- `**/logs/**`, `**/*.log` - Log files
- `**/tmp/**`, `**/temp/**` - Temporary files
- `**/.DS_Store` - macOS metadata (auto-regenerated)

---

## Database Operations Safety

**Transaction Requirements:**
- Use transactions for all batch inserts
- Never truncate tables without explicit backup
- Maintain referential integrity (foreign keys enabled)
- Test queries on subset before full scan

**Schema Changes:**
- Increment `schema_version` on any schema modification
- Create migration scripts in `modules/disk/migrations/`
- Backup database before applying migrations

**Performance:**
- Use prepared statements for repeated queries
- Batch inserts in groups of 1000
- Maintain indexes (already optimized for <4ms queries)
- Enable WAL mode (already configured)

---

## Module Structure

### Active Modules
- **`modules/disk/`** - Disk space management (CURRENT FOCUS)
  - Scanner: Parallel filesystem traversal with Merkle hashing
  - Analyzer: Change detection, growth tracking, duplicate detection
  - Cleanup: Safe deletion with Trash support and rollback

### Planned Modules (Future)
- **`modules/brew/`** - Homebrew package management
- **`modules/security/`** - Security audits and hardening
- **`modules/performance/`** - Performance monitoring and optimization
- **`modules/backups/`** - Backup status and verification

---

## Development Workflow for This Project

### For New Features

1. **Create Specification**
   - Location: `docs/specs/<feature-name>-spec.md`
   - Content: Architecture, requirements, edge cases
   - Format: Code-free, conceptual, Mermaid diagrams
   - **User approval required before proceeding**

2. **Write BDD Scenarios**
   - Location: `docs/features/<feature-name>.feature`
   - Format: Gherkin (Given/When/Then)
   - Coverage: Happy path, error cases, edge cases
   - **User approval required before proceeding**

3. **Implement Tests (TDD)**
   - Location: `tests/<module>/<feature>_test.py`
   - Write failing tests first
   - Cover scenarios from BDD

4. **Implement Code**
   - Follow approved specification exactly
   - No additional features without approval
   - Keep solutions simple and focused

5. **Update Documentation**
   - Update `STATUS.md` with progress
   - Update module README if needed
   - Commit with descriptive message

### For Scanner Implementation (Immediate Next Step)

**Phase 1: Specification**
- Document scanner architecture (threading model, Merkle trees)
- Define error handling strategy
- Specify performance requirements
- **Get approval before coding**

**Phase 2: BDD Scenarios**
- Successful full scan
- Incremental scan (Merkle hash comparison)
- Permission errors (graceful skip)
- Category detection (pattern matching)
- Progress reporting
- **Get approval before coding**

**Phase 3: TDD**
- Unit tests for directory traversal
- Tests for Merkle hash computation
- Tests for category matching
- Tests for database insertion

**Phase 4: Implementation**
- Python scanner with `ThreadPoolExecutor`
- Merkle hash computation (SHA256)
- SQLite batch inserts with transactions
- Progress callback system

**Phase 5: Validation**
- Test on limited scope (~/ first)
- Validate against BDD scenarios
- Expand to full system (/)
- Review results with user

---

## Technical Stack

**Languages:**
- Python 3.x - Core logic, scanner, analysis
- SQL - Database queries and schema
- Bash - System operations, integration scripts

**Database:**
- SQLite 3 with WAL mode
- Schema v1.0.0 deployed
- 7 tables + 4 views for analysis

**Tools:**
- Git for version control
- pytest for testing (when applicable)
- ThreadPoolExecutor for parallel scanning

---

## Current Project Status

### ✅ Complete
- Directory structure at `/Users/Shared/_claude_mac_manager`
- SQLite database schema (v1.0.0)
- 14 categories configured (node_modules, venvs, caches, etc.)
- 12 system exclusions (protected macOS paths)
- Documentation framework (README, STATUS, module docs)
- Git initialized (2 commits)
- Original cleanup script archived

### 🚧 In Progress
- This CLAUDE.md file

### ⏳ Pending
- Scanner specification + BDD scenarios
- Python scanner implementation
- Configuration files (YAML)
- Analysis engine
- CLI interface
- Cleanup automation

---

## Safety Framework

### Pre-Deletion Checklist
Before any file/directory deletion:
1. ✅ Verify category is marked `is_deletable = 1` in database
2. ✅ Confirm path NOT in protected paths list
3. ✅ Check restoration command is documented
4. ✅ Calculate and display space to be freed
5. ✅ Present dry-run preview to user
6. ✅ Require explicit user confirmation (not just Enter key)
7. ✅ Move to Trash (never permanent delete)
8. ✅ Log operation to `cleanup_history` table with trash path

### Error Handling Strategy
- **Permission Denied:** Skip directory, log warning, continue scan
- **Unreadable File:** Skip file, log error, continue scan
- **Database Error:** Rollback transaction, log error, stop operation
- **Disk Full:** Check available space before operations
- **Interrupted Scan:** Save partial results, allow resume

### Audit Trail Requirements
All operations must be logged:
- **Scans:** timestamp, duration, root path, file/directory counts
- **Deletions:** timestamp, target path, size, category, trash location
- **Errors:** timestamp, operation, error message, context
- **Restores:** timestamp, source (trash), destination, success status

---

## Performance Requirements

### Scanner Performance
- **Full scan (500GB):** < 5 minutes
- **Incremental scan:** < 30 seconds
- **Parallel threads:** 8 workers (optimal for SSD)
- **Memory usage:** < 500MB for typical home directory

### Database Performance
- **Query response:** < 4ms (already optimized with indexes)
- **Batch insert:** 1000 records per transaction
- **Database size:** ~10MB per 100,000 files scanned

### Responsiveness
- **Progress updates:** Every 1000 files
- **User interruption:** Graceful stop with partial results saved
- **Large directory warning:** Alert if directory > 10GB

---

## File Organization

```
/_claude_mac_manager/
├── CLAUDE.md                  # This file
├── README.md                  # Project overview
├── STATUS.md                  # Current progress tracking
├── modules/
│   └── disk/
│       ├── README.md          # Module documentation
│       ├── schema.sql         # Database schema
│       ├── scanner.py         # (pending) Filesystem scanner
│       ├── analyzer.py        # (pending) Analysis engine
│       └── cleanup.py         # (pending) Cleanup automation
├── data/
│   └── disk/
│       ├── cache.db           # SQLite database
│       └── history/           # Historical scan exports (JSON)
├── config/
│   ├── global.yaml            # (pending) System settings
│   └── disk/
│       ├── exclusions.yaml    # (pending) Custom exclusions
│       ├── categories.yaml    # (pending) Custom categories
│       └── profiles.yaml      # (pending) Scan profiles
├── docs/
│   ├── specs/                 # Specification documents
│   ├── features/              # BDD Gherkin scenarios
│       └── architecture.md    # System architecture
├── tests/                     # (pending) Test suite
├── scripts/
│   ├── cleanup_dependencies.sh  # Original manual cleanup script
│   └── utils/                 # Helper scripts
└── agents/                    # (pending) Claude Code specialized agents
```

---

## Next Immediate Actions

1. **Create scanner specification** (`docs/specs/scanner-spec.md`)
2. **Write BDD scenarios** (`docs/features/disk-scanning.feature`)
3. **Get user approval** on specifications
4. **Implement scanner** with TDD approach
5. **Run first system scan** and review results

---

## Attribution

**Author:** Vladimir K.S.
**Created:** 2025-11-24
**Project Start:** Foundation phase complete

**Related Documentation:**
- Global context: `~/.claude/CLAUDE.md`
- Project status: `STATUS.md`
- Disk module: `modules/disk/README.md`
