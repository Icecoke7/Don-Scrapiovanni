#!/bin/bash
# Script to remove specific files from git history
# This preserves most history but removes problematic files

set -e

echo "=========================================="
echo "Removing Files from Git History"
echo "=========================================="
echo ""
echo "This will remove the following files from ALL commits:"
echo "  - CONTAINER_EXPLANATION.md"
echo "  - COSMOS_DB_SETUP.md"
echo "  - WOHNTICKET_SETUP.md"
echo "  - WOHNTICKET_DEBUG.md"
echo "  - WOHNTICKET_STATUS.md"
echo "  - VIEW_DATA_IN_AZURE.md"
echo "  - setup_cosmos.sh"
echo "  - create_cosmos_containers.sh"
echo "  - get_connection_string.sh"
echo "  - check_wohnticket_status.sh"
echo "  - check_queue.sh"
echo "  - check_scrapers.sh"
echo "  - inspect_queue.py"
echo ""
echo "⚠️  WARNING: This will rewrite git history!"
echo "⚠️  Make sure you have a backup!"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

# Create backup
BACKUP_DIR="/root/GeWoScout-backup-$(date +%Y%m%d-%H%M%S)"
echo "Creating backup at: $BACKUP_DIR"
cp -r /root/GeWoScout "$BACKUP_DIR"
echo "✅ Backup created"

cd /root/GeWoScout

# List of files to remove from history
FILES_TO_REMOVE=(
    "CONTAINER_EXPLANATION.md"
    "COSMOS_DB_SETUP.md"
    "WOHNTICKET_SETUP.md"
    "WOHNTICKET_DEBUG.md"
    "WOHNTICKET_STATUS.md"
    "VIEW_DATA_IN_AZURE.md"
    "QUICK_START_COSMOS.md"
    "setup_cosmos.sh"
    "create_cosmos_containers.sh"
    "get_connection_string.sh"
    "check_wohnticket_status.sh"
    "check_queue.sh"
    "check_scrapers.sh"
    "inspect_queue.py"
    "STAATSOPER_SETUP.md"
    "SCRAPERS_SETUP.md"
    "SCRAPERS_QUICKSTART.md"
    "GITHUB_PUBLISHING_GUIDE.md"
    "GITHUB_SETUP_STEPS.md"
    "PRE_PUBLISH_CHECKLIST.md"
    "QUICK_SSH_SETUP.md"
    "YOUR_SSH_KEY.txt"
    "setup_github_ssh.sh"
)

# Build the filter command
FILTER_CMD="git rm --cached --ignore-unmatch"
for file in "${FILES_TO_REMOVE[@]}"; do
    FILTER_CMD="$FILTER_CMD \"$file\""
done

echo ""
echo "Step 1: Removing files from all commits..."
echo "This may take a few minutes..."

# Use git filter-branch to remove files
git filter-branch --force --index-filter "$FILTER_CMD" --prune-empty --tag-name-filter cat -- --all

echo "✅ Files removed from history"

echo ""
echo "Step 2: Cleaning up references..."
rm -rf .git/refs/original/
git reflog expire --expire=now --all
git gc --prune=now --aggressive

echo "✅ Cleanup complete"

echo ""
echo "Step 3: Verifying..."
echo "Checking if files still exist in history..."

FOUND_FILES=0
for file in "${FILES_TO_REMOVE[@]}"; do
    if git log --all --full-history --oneline -- "$file" | head -1 > /dev/null 2>&1; then
        echo "  ⚠️  Still found: $file"
        FOUND_FILES=1
    fi
done

if [ $FOUND_FILES -eq 0 ]; then
    echo "✅ All files successfully removed from history"
else
    echo "⚠️  Some files may still exist in history"
fi

echo ""
echo "=========================================="
echo "Done!"
echo "=========================================="
echo ""
echo "Backup is at: $BACKUP_DIR"
echo ""
echo "Next steps:"
echo "1. Review the changes: git log --oneline"
echo "2. Verify no gewoscout references:"
echo "   git log --all --full-history -p | grep -i gewoscout"
echo "3. If everything looks good, push to GitHub:"
echo "   git push -f origin main"
echo ""
echo "⚠️  WARNING: Force push will overwrite remote history!"
echo "   Make sure no one else is using this repository."
echo ""
