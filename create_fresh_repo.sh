#!/bin/bash
# Script to create a fresh repository without gewoscout references in history
# This will create a new clean repository with only current files

set -e

echo "=========================================="
echo "Creating Fresh Repository"
echo "=========================================="
echo ""
echo "This script will:"
echo "1. Create a backup of your current repo"
echo "2. Create a fresh git repository with only current files"
echo "3. Remove all gewoscout references from history"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

# Get the current remote URL
CURRENT_REMOTE=$(git remote get-url origin 2>/dev/null || echo "")
BACKUP_DIR="/root/GeWoScout-backup-$(date +%Y%m%d-%H%M%S)"
FRESH_REPO_DIR="/root/GeWoScout-fresh"

echo "Step 1: Creating backup..."
cp -r /root/GeWoScout "$BACKUP_DIR"
echo "✅ Backup created at: $BACKUP_DIR"

echo ""
echo "Step 2: Creating fresh repository..."
cd /root/GeWoScout

# Remove .git directory
rm -rf .git

# Initialize fresh git repo
git init
git branch -M main

# Add all current files
git add .

# Create initial commit
git commit -m "Initial commit - Clean repository"

echo "✅ Fresh repository created"

echo ""
echo "Step 3: Setting up remote..."
if [ -n "$CURRENT_REMOTE" ]; then
    echo "Current remote: $CURRENT_REMOTE"
    read -p "Use same remote? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git remote add origin "$CURRENT_REMOTE"
        echo "✅ Remote added: $CURRENT_REMOTE"
        echo ""
        echo "⚠️  IMPORTANT: To push this fresh repo, you'll need to force push:"
        echo "   git push -f origin main"
        echo ""
        echo "⚠️  WARNING: This will overwrite the remote repository history!"
        echo "   Make sure you have a backup and that no one else is using this repo."
    else
        echo "Skipped remote setup. Add it manually with:"
        echo "   git remote add origin <your-repo-url>"
    fi
else
    echo "No remote found. Add it manually with:"
    echo "   git remote add origin <your-repo-url>"
fi

echo ""
echo "=========================================="
echo "Done!"
echo "=========================================="
echo ""
echo "Your fresh repository is ready at: /root/GeWoScout"
echo "Backup is at: $BACKUP_DIR"
echo ""
echo "Next steps:"
echo "1. Review the fresh repo: cd /root/GeWoScout && git log"
echo "2. Verify no gewoscout references: grep -ri gewoscout . --exclude-dir=.git"
echo "3. If everything looks good, push to GitHub:"
echo "   git push -f origin main"
echo ""
