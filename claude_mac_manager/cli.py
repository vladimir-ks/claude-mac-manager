"""
Claude Mac Manager - Command Line Interface

Entry point for the `cmm` command-line tool.

Commands:
    cmm --version           Show version information
    cmm scan                Run filesystem scan
    cmm status              Display summary
    cmm analyze             Generate recommendations
    cmm cleanup             Interactive cleanup (dry-run default)
    cmm config              Configuration management

Author: Vladimir K.S.
"""

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from . import __version__, DATA_DIR, DATABASE_PATH
from .safety import validate_deletion, get_deletable_categories

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="Claude Mac Manager")
@click.pass_context
def cli(ctx: click.Context) -> None:
    """
    Claude Mac Manager - Comprehensive macOS system management toolkit.

    A safety-first system management tool for disk space analysis, cleanup automation,
    and system optimization.

    \b
    Features:
    - Disk space analysis with parallel scanning
    - Safe cleanup with Trash-based deletion
    - Multi-layer safety protection
    - Claude Code integration
    - Comprehensive audit logging

    \b
    Safety Guarantees:
    - Dry-run mode by default (preview before deletion)
    - Protected paths (System, Documents, .git, etc.)
    - Trash-based deletion (30-day recovery window)
    - Comprehensive audit trail

    \b
    Examples:
        cmm scan --profile quick    # Scan home directory
        cmm status                  # View summary
        cmm analyze                 # Get recommendations
        cmm cleanup --dry-run       # Preview cleanup

    \b
    Project: https://github.com/vladimir-ks/claude-mac-manager
    Author: Vladimir K.S.
    """
    # Ensure context object exists
    ctx.ensure_object(dict)


@cli.command()
def version() -> None:
    """Display version information and system details."""
    console.print(f"[bold blue]Claude Mac Manager[/bold blue] v{__version__}")
    console.print(f"Data Directory: {DATA_DIR}")
    console.print(f"Database: {DATABASE_PATH}")
    console.print(f"Database Exists: {'✓' if DATABASE_PATH.exists() else '✗'}")
    console.print("\n[dim]A safety-first macOS system management toolkit[/dim]")


@cli.command()
@click.option(
    "--profile",
    type=click.Choice(["quick", "full", "custom"], case_sensitive=False),
    default="full",
    help="Scan profile (quick=home only, full=entire system)"
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=True,
    help="Preview scan without storing results (default: True)"
)
def scan(profile: str, dry_run: bool) -> None:
    """
    Run filesystem scan to analyze disk usage.

    Scans your Mac's filesystem and stores results in the database for analysis.
    Supports different scan profiles for speed vs. completeness tradeoffs.

    \b
    Profiles:
        quick:  Scan home directory only (~5-10 minutes)
        full:   Scan entire system (~10-20 minutes)
        custom: Use custom configuration

    \b
    Examples:
        cmm scan --profile quick     # Fast scan of home directory
        cmm scan --profile full      # Complete system scan
        cmm scan --dry-run           # Preview what would be scanned
    """
    console.print(f"[bold]Scanning with profile: {profile}[/bold]")

    if dry_run:
        console.print("[yellow]DRY-RUN MODE:[/yellow] Preview only, no data stored")

    # TODO: Implement scanner
    console.print("[red]Scanner not yet implemented[/red]")
    console.print("This will be implemented in the next phase.")


@cli.command()
@click.option(
    "--format",
    type=click.Choice(["table", "json"], case_sensitive=False),
    default="table",
    help="Output format"
)
def status(format: str) -> None:
    """
    Display disk usage summary from last scan.

    Shows overview of disk usage, deletable space by category, and largest directories.

    \b
    Examples:
        cmm status                  # Display summary table
        cmm status --format json    # Output as JSON
    """
    if not DATABASE_PATH.exists():
        console.print("[red]Error:[/red] Database not found. Run 'cmm scan' first.")
        sys.exit(1)

    console.print("[bold]Disk Usage Summary[/bold]\n")

    # Display deletable categories
    categories = get_deletable_categories()

    if format == "table":
        table = Table(title="Deletable Categories")
        table.add_column("Category", style="cyan")
        table.add_column("Description", style="white")
        table.add_column("Restoration", style="green")
        table.add_column("Priority", justify="right", style="yellow")

        for cat in categories:
            table.add_row(
                cat["name"],
                cat["description"],
                cat["restoration_command"],
                str(cat["priority"])
            )

        console.print(table)
    else:
        import json
        console.print(json.dumps(categories, indent=2))

    console.print("\n[dim]Note: Scanner implementation pending. Full stats coming soon.[/dim]")


@cli.command()
def analyze() -> None:
    """
    Generate cleanup recommendations based on scan results.

    Analyzes scan data and provides prioritized recommendations for safe cleanup.

    \b
    Examples:
        cmm analyze              # Show recommendations
    """
    if not DATABASE_PATH.exists():
        console.print("[red]Error:[/red] Database not found. Run 'cmm scan' first.")
        sys.exit(1)

    console.print("[bold]Analysis & Recommendations[/bold]\n")

    # TODO: Implement analyzer
    console.print("[red]Analyzer not yet implemented[/red]")
    console.print("This will be implemented after scanner is complete.")


@cli.command()
@click.option(
    "--dry-run/--no-dry-run",
    default=True,
    help="Preview changes without deleting (default: True)"
)
@click.option(
    "--category",
    type=str,
    help="Target specific category (e.g., node_modules, venv)"
)
@click.option(
    "--path",
    type=click.Path(exists=True),
    help="Target specific path"
)
def cleanup(dry_run: bool, category: str, path: str) -> None:
    """
    Interactive cleanup with safety checks.

    Safely delete files/directories based on analysis recommendations.
    Defaults to dry-run mode for safety.

    \b
    Safety Features:
    - Dry-run mode by default (preview before deletion)
    - Protected paths never deleted
    - Trash-based deletion (30-day recovery)
    - Explicit confirmation required
    - Comprehensive audit logging

    \b
    Examples:
        cmm cleanup --dry-run                        # Preview cleanup
        cmm cleanup --category node_modules          # Clean all node_modules
        cmm cleanup --path ~/project/node_modules    # Clean specific path
        cmm cleanup --no-dry-run                     # Real deletion (WARNING!)
    """
    if not DATABASE_PATH.exists():
        console.print("[red]Error:[/red] Database not found. Run 'cmm scan' first.")
        sys.exit(1)

    if dry_run:
        console.print("[yellow]DRY-RUN MODE:[/yellow] Preview only, no actual deletion\n")
    else:
        console.print("[red]REAL DELETION MODE:[/red] Files will be moved to Trash\n")

    if path:
        # Validate specific path
        result = validate_deletion(path, category, dry_run=dry_run)

        if result.valid:
            console.print(f"[green]✓[/green] Path is safe to delete: {result.path}")
            console.print(f"  Category: {result.category or 'Unknown'}")
            console.print(f"  Size: {result.size_bytes:,} bytes")
            if result.restoration_command:
                console.print(f"  Restore: {result.restoration_command}")

            if result.warnings:
                console.print("\n[yellow]Warnings:[/yellow]")
                for warning in result.warnings:
                    console.print(f"  - {warning}")

            if not dry_run:
                # TODO: Implement actual deletion
                console.print("\n[red]Actual deletion not yet implemented[/red]")
        else:
            console.print(f"[red]✗[/red] Path NOT safe to delete: {result.path}")
            console.print("\n[red]Errors:[/red]")
            for error in result.errors:
                console.print(f"  - {error}")
    else:
        console.print("Interactive cleanup mode not yet implemented.")
        console.print("Please specify --path for now.")


@cli.command()
@click.option(
    "--list",
    "list_config",
    is_flag=True,
    help="List current configuration"
)
def config(list_config: bool) -> None:
    """
    Manage configuration settings.

    View and modify Claude Mac Manager configuration.

    \b
    Examples:
        cmm config --list           # Show current config
    """
    if list_config:
        console.print("[bold]Configuration[/bold]\n")
        console.print(f"Data Directory: {DATA_DIR}")
        console.print(f"Database: {DATABASE_PATH}")
        console.print(f"Version: {__version__}")
    else:
        console.print("Configuration management not yet fully implemented.")
        console.print("Use --list to view current settings.")


def main() -> None:
    """Main entry point for CLI."""
    try:
        cli(obj={})
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
