#!/bin/bash
# Safe Dependency Cleanup Script
# Generated: 2025-11-24
# Author: Vladimir K.S.

set -e  # Exit on error

echo "=================================================="
echo "Safe Dependency Cleanup Script"
echo "=================================================="
echo ""

# Track total space freed
TOTAL_FREED=0

# Function to safely delete and report
safe_delete() {
    local path="$1"
    local desc="$2"

    if [ -d "$path" ]; then
        # Get size before deletion
        SIZE=$(du -sh "$path" 2>/dev/null | cut -f1)
        echo "🗑️  Deleting: $desc"
        echo "    Location: $path"
        echo "    Size: $SIZE"

        rm -rf "$path"

        if [ ! -d "$path" ]; then
            echo "    ✅ Deleted successfully"
        else
            echo "    ❌ Failed to delete"
        fi
        echo ""
    else
        echo "⏭️  Skipping: $desc (not found)"
        echo "    Location: $path"
        echo ""
    fi
}

echo "Phase 2: Cleaning Node.js Dependencies"
echo "--------------------------------------"
safe_delete "/Users/vmks/02Ainamnes/ainamnes_back/node_modules" "ainamnes_back node_modules (735 MB)"
safe_delete "/Users/vmks/115_LogosForge/LogosForge/node_modules" "LogosForge node_modules (616 MB)"
safe_delete "/Users/vmks/06_actiQR/node_modules" "actiQR node_modules (555 MB)"
safe_delete "/Users/vmks/50_n8n/prado_task_manager/gsheets_schema_extractor_tool/node_modules" "gsheets_extractor node_modules (124 MB)"

echo "Phase 3: Cleaning Python Virtual Environments"
echo "--------------------------------------"
safe_delete "/Users/vmks/02Ainamnes/ainamnes_infra/.venv" "ainamnes_infra venv (474 MB)"
safe_delete "/Users/vmks/02Ainamnes/Vasilisa-case/.venv" "Vasilisa-case venv (394 MB)"

echo "Phase 4: Cleaning Archived Projects"
echo "--------------------------------------"
safe_delete "/Users/vmks/_dev_tools/claude-skills-builder-vladks/.claude/skills/tmux-orchestration/.trash/archive/pneuma-claude-hooks" "Archived pneuma-claude-hooks (88 MB)"

echo "=================================================="
echo "Cleanup Complete!"
echo "=================================================="
echo ""
echo "Already cleaned by Claude:"
echo "  ✅ NPM cache (~/.npm/_npx): 1.4 GB"
echo "  ✅ Gemini history: 360 MB"
echo ""
echo "Run this script again to verify all deletions succeeded."
echo ""
echo "To restore dependencies when needed:"
echo "  - Node.js projects: cd <project> && npm install"
echo "  - Python projects: cd <project> && pip install -r requirements.txt"
echo "  - Poetry projects: cd <project> && poetry install"
