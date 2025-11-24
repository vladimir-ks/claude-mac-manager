"""
Post-Installation Script

Runs automatically after `pipx install claude-mac-manager` to:
1. Verify data directory exists
2. Initialize database if needed
3. Detect and install Claude Code plugin (if Claude Code is present)
4. Create convenience symlinks
5. Display installation success message

Author: Vladimir K.S.
"""

import os
import shutil
import sqlite3
import sys
from pathlib import Path

from . import __version__, DATA_DIR, DATABASE_PATH


def check_directory_writable(directory: Path) -> bool:
    """Check if directory is writable."""
    return os.access(directory, os.W_OK)


def ensure_data_directory() -> bool:
    """
    Ensure data directory exists and is writable.

    Returns:
        True if directory is ready, False otherwise
    """
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        (DATA_DIR / "data" / "disk").mkdir(parents=True, exist_ok=True)
        (DATA_DIR / "data" / "disk" / "history").mkdir(parents=True, exist_ok=True)
        (DATA_DIR / "config" / "disk").mkdir(parents=True, exist_ok=True)

        if not check_directory_writable(DATA_DIR):
            print(f"⚠️  Warning: Data directory not writable: {DATA_DIR}")
            return False

        return True

    except Exception as e:
        print(f"❌ Error creating data directory: {e}")
        return False


def initialize_database() -> bool:
    """
    Initialize database if it doesn't exist.

    Returns:
        True if database is ready, False on error
    """
    if DATABASE_PATH.exists():
        print(f"✓ Database already exists: {DATABASE_PATH}")
        return True

    try:
        # Check if schema.sql exists
        schema_file = Path(__file__).parent.parent / "modules" / "disk" / "schema.sql"

        if not schema_file.exists():
            print(f"⚠️  Schema file not found: {schema_file}")
            print("   Database will be initialized on first scan.")
            return True

        # Read and execute schema
        with open(schema_file, 'r') as f:
            schema_sql = f.read()

        conn = sqlite3.connect(DATABASE_PATH)
        conn.executescript(schema_sql)
        conn.close()

        print(f"✓ Database initialized: {DATABASE_PATH}")
        return True

    except Exception as e:
        print(f"⚠️  Could not initialize database: {e}")
        print("   Database will be initialized on first scan.")
        return True  # Non-fatal error


def detect_claude_code() -> bool:
    """
    Detect if Claude Code is installed.

    Returns:
        True if Claude Code is detected, False otherwise
    """
    claude_dir = Path.home() / ".claude"
    return claude_dir.exists() and claude_dir.is_dir()


def install_claude_code_plugin() -> bool:
    """
    Install Claude Code plugin if Claude Code is detected.

    Returns:
        True if plugin installed successfully, False otherwise
    """
    if not detect_claude_code():
        return False

    try:
        claude_plugins_dir = Path.home() / ".claude" / "plugins"
        claude_plugins_dir.mkdir(parents=True, exist_ok=True)

        plugin_source = DATA_DIR / ".claude-plugin"
        plugin_dest = claude_plugins_dir / "claude-mac-manager"

        if plugin_source.exists():
            if plugin_dest.exists():
                # Remove old version
                if plugin_dest.is_symlink():
                    plugin_dest.unlink()
                elif plugin_dest.is_dir():
                    shutil.rmtree(plugin_dest)

            # Create symlink
            plugin_dest.symlink_to(plugin_source)
            print(f"✓ Claude Code plugin installed: {plugin_dest}")
            print("  Restart Claude Code to activate the plugin.")
            return True
        else:
            print("⚠️  Plugin source not found (will be added in future release)")
            return False

    except Exception as e:
        print(f"⚠️  Could not install Claude Code plugin: {e}")
        return False


def create_home_symlink() -> bool:
    """
    Create convenience symlink in user's home directory.

    Returns:
        True if symlink created, False otherwise
    """
    try:
        home_link = Path.home() / "claude_mac_manager"

        if home_link.exists():
            if home_link.is_symlink() and home_link.resolve() == DATA_DIR:
                # Symlink already correct
                return True
            else:
                # Remove old link/directory
                if home_link.is_symlink():
                    home_link.unlink()
                elif home_link.is_dir():
                    print(f"⚠️  Directory already exists: {home_link}")
                    print(f"   Please remove it manually to create symlink.")
                    return False

        home_link.symlink_to(DATA_DIR)
        print(f"✓ Convenience symlink created: {home_link} -> {DATA_DIR}")
        return True

    except Exception as e:
        print(f"⚠️  Could not create symlink: {e}")
        return False


def post_install() -> None:
    """
    Main post-installation routine.

    This function is called automatically by pipx after installation.
    """
    print("\n" + "=" * 70)
    print(f"  Claude Mac Manager v{__version__} - Post-Install")
    print("=" * 70 + "\n")

    # Step 1: Ensure data directory
    print("📁 Setting up data directory...")
    if not ensure_data_directory():
        print("\n❌ Installation incomplete: Could not create data directory")
        print(f"   Please manually create: {DATA_DIR}")
        sys.exit(1)

    # Step 2: Initialize database
    print("\n💾 Initializing database...")
    initialize_database()

    # Step 3: Claude Code integration
    print("\n🔌 Checking for Claude Code...")
    if detect_claude_code():
        print("✓ Claude Code detected")
        install_claude_code_plugin()
    else:
        print("  Claude Code not detected (optional)")

    # Step 4: Create convenience symlink
    print("\n🔗 Creating convenience symlink...")
    create_home_symlink()

    # Step 5: Success message
    print("\n" + "=" * 70)
    print("  ✅ Installation Complete!")
    print("=" * 70)

    print("\n📋 Quick Start:")
    print("   cmm --version           # Verify installation")
    print("   cmm status              # View deletable categories")
    print("   cmm scan --profile quick    # Scan home directory (coming soon)")
    print("   cmm cleanup --dry-run       # Preview cleanup (coming soon)")

    print("\n📂 Locations:")
    print(f"   Data:     {DATA_DIR}")
    print(f"   Database: {DATABASE_PATH}")
    print(f"   Shortcut: ~/claude_mac_manager -> {DATA_DIR}")

    print("\n📚 Documentation:")
    print("   GitHub:  https://github.com/vladimir-ks/claude-mac-manager")
    print("   README:  " + str(DATA_DIR / "README.md"))

    print("\n⚠️  Safety Reminders:")
    print("   • All deletions go to Trash (30-day recovery)")
    print("   • Dry-run mode is default (preview before delete)")
    print("   • Protected paths are never deleted (System, Documents, .git, etc.)")
    print("   • Full audit trail in database")

    print("\n💡 Next Steps:")
    print("   1. Review configuration: cmm config --list")
    print("   2. Check deletable categories: cmm status")
    print("   3. Wait for scanner implementation (coming soon!)")

    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    post_install()
