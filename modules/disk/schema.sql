-- Claude Mac Manager - Disk Module Database Schema
-- Author: Vladimir K.S.
-- Created: 2025-11-24
-- Purpose: Fast disk analysis with Merkle tree-based change detection

-- ====================
-- SCANS TABLE
-- ====================
-- Tracks each full or incremental scan
CREATE TABLE IF NOT EXISTS scans (
    scan_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    duration_seconds REAL,
    root_path TEXT NOT NULL,
    scan_type TEXT CHECK(scan_type IN ('full', 'incremental')) DEFAULT 'full',
    total_files INTEGER,
    total_directories INTEGER,
    total_size_bytes INTEGER,
    merkle_root_hash TEXT,
    exclusion_patterns TEXT,  -- JSON array of patterns used
    notes TEXT
);

CREATE INDEX idx_scans_timestamp ON scans(timestamp DESC);
CREATE INDEX idx_scans_root_path ON scans(root_path);

-- ====================
-- DIRECTORIES TABLE
-- ====================
-- Stores directory metadata with Merkle hashes for change detection
CREATE TABLE IF NOT EXISTS directories (
    directory_id INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_id INTEGER NOT NULL,
    path TEXT NOT NULL,
    parent_path TEXT,
    name TEXT NOT NULL,
    size_bytes INTEGER DEFAULT 0,
    file_count INTEGER DEFAULT 0,
    subdirectory_count INTEGER DEFAULT 0,
    last_modified DATETIME,
    last_scanned DATETIME DEFAULT CURRENT_TIMESTAMP,
    merkle_hash TEXT,  -- Hash of this directory's content + children hashes
    category TEXT,  -- node_modules, venv, cache, logs, etc.
    is_deletable BOOLEAN DEFAULT 0,
    FOREIGN KEY (scan_id) REFERENCES scans(scan_id) ON DELETE CASCADE
);

CREATE UNIQUE INDEX idx_directories_path_scan ON directories(path, scan_id);
CREATE INDEX idx_directories_parent ON directories(parent_path);
CREATE INDEX idx_directories_size ON directories(size_bytes DESC);
CREATE INDEX idx_directories_category ON directories(category);
CREATE INDEX idx_directories_deletable ON directories(is_deletable);
CREATE INDEX idx_directories_hash ON directories(merkle_hash);

-- ====================
-- FILES TABLE
-- ====================
-- Stores file metadata for large files and special cases
CREATE TABLE IF NOT EXISTS files (
    file_id INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_id INTEGER NOT NULL,
    path TEXT NOT NULL,
    directory_path TEXT NOT NULL,
    name TEXT NOT NULL,
    extension TEXT,
    size_bytes INTEGER DEFAULT 0,
    last_modified DATETIME,
    content_hash TEXT,  -- SHA256 for duplicate detection
    is_large BOOLEAN DEFAULT 0,  -- Files > 100MB
    is_duplicate BOOLEAN DEFAULT 0,
    FOREIGN KEY (scan_id) REFERENCES scans(scan_id) ON DELETE CASCADE
);

CREATE UNIQUE INDEX idx_files_path_scan ON files(path, scan_id);
CREATE INDEX idx_files_directory ON files(directory_path);
CREATE INDEX idx_files_size ON files(size_bytes DESC);
CREATE INDEX idx_files_extension ON files(extension);
CREATE INDEX idx_files_hash ON files(content_hash);
CREATE INDEX idx_files_large ON files(is_large);
CREATE INDEX idx_files_duplicate ON files(is_duplicate);

-- ====================
-- CATEGORIES TABLE
-- ====================
-- Classification rules for different types of directories/files
CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    patterns TEXT NOT NULL,  -- JSON array of glob patterns
    is_deletable BOOLEAN DEFAULT 0,
    restoration_command TEXT,  -- How to restore (e.g., "npm install")
    color TEXT,  -- UI color code for reports
    priority INTEGER DEFAULT 0  -- Cleanup priority (higher = more important)
);

-- Insert default categories
INSERT OR IGNORE INTO categories (name, description, patterns, is_deletable, restoration_command, color, priority) VALUES
('node_modules', 'Node.js dependencies', '["**/node_modules"]', 1, 'npm install', '#E8274B', 90),
('python_venv', 'Python virtual environments', '["**/.venv", "**/venv", "**/env"]', 1, 'pip install -r requirements.txt OR poetry install', '#3776AB', 85),
('npm_cache', 'NPM cache directories', '["~/.npm/_npx/**", "**/.npm/**"]', 1, 'Auto-regenerated', '#CB3837', 95),
('gem_cache', 'Ruby gem caches', '["~/.gem/cache/**", "**/vendor/cache/**"]', 1, 'bundle install', '#CC342D', 70),
('cargo_target', 'Rust build artifacts', '["**/target"]', 1, 'cargo build', '#CE422B', 75),
('go_cache', 'Go build cache', '["~/.cache/go-build/**", "**/pkg/mod/**"]', 1, 'go build', '#00ADD8', 70),
('python_cache', 'Python bytecode cache', '["**/__pycache__", "**/*.pyc", "**/*.pyo"]', 1, 'Auto-regenerated', '#3776AB', 80),
('logs', 'Log files', '["**/*.log", "**/logs/**", "**/_logs/**"]', 1, 'N/A', '#888888', 60),
('temp', 'Temporary files', '["**/tmp/**", "**/temp/**", "**/.tmp/**"]', 1, 'N/A', '#FFA500', 65),
('ds_store', 'macOS metadata', '["**/.DS_Store"]', 1, 'Auto-regenerated', '#A2AAAD', 50),
('git_history', 'Git repositories', '["**/.git"]', 0, 'N/A - DO NOT DELETE', '#F05032', 0),
('system', 'System directories', '["/System/**", "/bin/**", "/sbin/**", "/usr/**"]', 0, 'N/A - PROTECTED', '#000000', 0),
('applications', 'Installed applications', '["/Applications/**"]', 0, 'Manual reinstall', '#0071E3', 0),
('documents', 'User documents', '["~/Documents/**", "~/Desktop/**", "~/Downloads/**"]', 0, 'N/A - USER DATA', '#34C759', 0);

-- ====================
-- EXCLUSIONS TABLE
-- ====================
-- Directories/patterns to skip during scanning
CREATE TABLE IF NOT EXISTS exclusions (
    exclusion_id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern TEXT UNIQUE NOT NULL,
    reason TEXT,
    is_active BOOLEAN DEFAULT 1
);

-- Insert default exclusions (macOS system directories)
INSERT OR IGNORE INTO exclusions (pattern, reason, is_active) VALUES
('/dev', 'Virtual filesystem', 1),
('/proc', 'Virtual filesystem', 1),
('/sys', 'Virtual filesystem', 1),
('/private/var/vm', 'Virtual memory swap', 1),
('/Volumes', 'Mounted volumes (scan separately)', 1),
('/System/Volumes', 'System volume groups', 1),
('/.Spotlight-V100', 'Spotlight index', 1),
('/.fseventsd', 'Filesystem events', 1),
('/.TemporaryItems', 'macOS temporary', 1),
('/.Trashes', 'Trash directories', 1),
('/Library/Caches', 'System caches (large, auto-managed)', 1),
('/private/tmp', 'System temporary', 1);

-- ====================
-- CLEANUP_HISTORY TABLE
-- ====================
-- Track all cleanup operations for rollback
CREATE TABLE IF NOT EXISTS cleanup_history (
    cleanup_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    target_path TEXT NOT NULL,
    size_bytes INTEGER,
    category TEXT,
    action TEXT CHECK(action IN ('trash', 'delete', 'rollback')) DEFAULT 'trash',
    success BOOLEAN DEFAULT 0,
    error_message TEXT,
    trash_path TEXT,  -- Where it was moved in Trash
    can_restore BOOLEAN DEFAULT 1
);

CREATE INDEX idx_cleanup_timestamp ON cleanup_history(timestamp DESC);
CREATE INDEX idx_cleanup_target ON cleanup_history(target_path);
CREATE INDEX idx_cleanup_category ON cleanup_history(category);

-- ====================
-- GROWTH_TRACKING TABLE
-- ====================
-- Track size changes over time for trend analysis
CREATE TABLE IF NOT EXISTS growth_tracking (
    tracking_id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT NOT NULL,
    category TEXT,
    scan_id INTEGER NOT NULL,
    size_bytes INTEGER,
    file_count INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    growth_rate_mb_per_day REAL,  -- Calculated from previous scan
    FOREIGN KEY (scan_id) REFERENCES scans(scan_id) ON DELETE CASCADE
);

CREATE INDEX idx_growth_path ON growth_tracking(path);
CREATE INDEX idx_growth_timestamp ON growth_tracking(timestamp DESC);
CREATE INDEX idx_growth_rate ON growth_tracking(growth_rate_mb_per_day DESC);

-- ====================
-- VIEWS
-- ====================

-- Latest scan summary
CREATE VIEW IF NOT EXISTS v_latest_scan AS
SELECT * FROM scans ORDER BY timestamp DESC LIMIT 1;

-- Top 100 largest directories
CREATE VIEW IF NOT EXISTS v_largest_directories AS
SELECT
    d.path,
    d.category,
    d.size_bytes,
    ROUND(d.size_bytes / 1024.0 / 1024.0 / 1024.0, 2) as size_gb,
    d.file_count,
    d.is_deletable,
    c.restoration_command
FROM directories d
LEFT JOIN categories c ON d.category = c.name
WHERE d.scan_id = (SELECT scan_id FROM v_latest_scan)
ORDER BY d.size_bytes DESC
LIMIT 100;

-- Deletable space summary by category
CREATE VIEW IF NOT EXISTS v_deletable_summary AS
SELECT
    d.category,
    COUNT(*) as directory_count,
    SUM(d.size_bytes) as total_bytes,
    ROUND(SUM(d.size_bytes) / 1024.0 / 1024.0 / 1024.0, 2) as total_gb,
    c.restoration_command
FROM directories d
LEFT JOIN categories c ON d.category = c.name
WHERE d.is_deletable = 1
  AND d.scan_id = (SELECT scan_id FROM v_latest_scan)
GROUP BY d.category
ORDER BY total_bytes DESC;

-- Duplicate files
CREATE VIEW IF NOT EXISTS v_duplicate_files AS
SELECT
    content_hash,
    COUNT(*) as duplicate_count,
    SUM(size_bytes) as wasted_bytes,
    ROUND(SUM(size_bytes) / 1024.0 / 1024.0, 2) as wasted_mb,
    GROUP_CONCAT(path, ' | ') as file_paths
FROM files
WHERE scan_id = (SELECT scan_id FROM v_latest_scan)
  AND content_hash IS NOT NULL
GROUP BY content_hash
HAVING duplicate_count > 1
ORDER BY wasted_bytes DESC;

-- Growth trends (last 10 scans)
CREATE VIEW IF NOT EXISTS v_growth_trends AS
SELECT
    path,
    category,
    AVG(growth_rate_mb_per_day) as avg_growth_mb_per_day,
    MAX(size_bytes) as peak_size_bytes,
    MIN(size_bytes) as min_size_bytes
FROM growth_tracking
WHERE scan_id IN (
    SELECT scan_id FROM scans ORDER BY timestamp DESC LIMIT 10
)
GROUP BY path, category
HAVING avg_growth_mb_per_day > 0
ORDER BY avg_growth_mb_per_day DESC;

-- ====================
-- PERFORMANCE
-- ====================

-- Enable Write-Ahead Logging for better concurrency
PRAGMA journal_mode=WAL;

-- Increase cache size (10MB)
PRAGMA cache_size=-10000;

-- Optimize for speed
PRAGMA synchronous=NORMAL;
PRAGMA temp_store=MEMORY;

-- ====================
-- METADATA
-- ====================

CREATE TABLE IF NOT EXISTS schema_version (
    version TEXT PRIMARY KEY,
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO schema_version (version) VALUES ('1.0.0');
