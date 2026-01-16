#!/bin/bash
# Script to create a fresh repository without gewoscout references in history
# Non-interactive version - automatically uses current remote

set -e

echo "=========================================="
echo "Creating Fresh Repository"
echo "=========================================="
echo ""

# Get the current remote URL
CURRENT_REMOTE=$(git remote get-url origin 2>/dev/null || echo "")

if [ -z "$CURRENT_REMOTE" ]; then
    echo "❌ Error: No remote 'origin' found"
    echo "Please add a remote first: git remote add origin <url>"
    exit 1
fi

echo "Current remote: $CURRENT_REMOTE"
echo ""

# Create backup
BACKUP_DIR="/root/GeWoScout-backup-$(date +%Y%m%d-%H%M%S)"
echo "Step 1: Creating backup..."
cp -r /root/GeWoScout "$BACKUP_DIR"
echo "✅ Backup created at: $BACKUP_DIR"
echo ""

# Remove .git directory
echo "Step 2: Removing old git history..."
rm -rf .git
echo "✅ Old git history removed"
echo ""

# Initialize fresh git repo
echo "Step 3: Initializing fresh repository..."
git init
git branch -M main
echo "✅ Fresh repository initialized"
echo ""

# Add all current files
echo "Step 4: Adding current files..."
git add .
echo "✅ Files added"
echo ""

# Create initial commit
echo "Step 5: Creating initial commit..."
git commit -m "Initial commit - Clean repository"
echo "✅ Initial commit created"
echo ""

# Set up remote
echo "Step 6: Setting up remote..."
git remote add origin "$CURRENT_REMOTE"
echo "✅ Remote added: $CURRENT_REMOTE"
echo ""

echo "=========================================="
echo "Fresh Repository Created Successfully!"
echo "=========================================="
echo ""
echo "Backup location: $BACKUP_DIR"
echo "Remote: $CURRENT_REMOTE"
echo ""
echo "Next steps:"
echo "1. Verify the repository:"
echo "   git log"
echo "   # Should show one commit: 'Initial commit...'"
echo ""
echo "2. Verify no gewoscout references:"
echo "   grep -ri gewoscout . --exclude-dir=.git"
echo "   # Should return nothing"
echo ""
echo "3. Push to GitHub (this will overwrite remote history):"
echo "   git push -f origin main"
echo ""
echo "⚠️  WARNING: The force push will overwrite your GitHub repository history!"
echo "   Make sure you're ready before running the push command."
echo ""
