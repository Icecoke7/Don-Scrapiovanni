# Removing Files from GitHub History

This guide explains how to remove files with "gewoscout" references from your GitHub repository history.

## The Problem

Files like `CONTAINER_EXPLANATION.md` and `COSMOS_DB_SETUP.md` were committed to git with references to "gewoscout" (like `gewoscout-db`, `gewoscout-rg`, `gewoscout-cosmos`). Even though these files are now deleted, they still exist in git history and are visible on GitHub.

## Solution Options

### Option 1: Fresh Repository (Recommended - Simplest)

This creates a completely new git history with only your current clean files.

**Pros:**
- ✅ Simplest and safest
- ✅ Complete clean history
- ✅ No risk of breaking existing workflows

**Cons:**
- ⚠️ Loses git history (but you have a backup)
- ⚠️ Requires force push to GitHub

**Steps:**

1. Run the script:
   ```bash
   ./create_fresh_repo.sh
   ```

2. Review the fresh repository:
   ```bash
   cd /root/GeWoScout
   git log
   # Should only show one commit: "Initial commit - Clean repository..."
   ```

3. Verify no gewoscout references:
   ```bash
   grep -ri gewoscout . --exclude-dir=.git
   # Should return nothing
   ```

4. Push to GitHub (force push required):
   ```bash
   git push -f origin main
   ```

   ⚠️ **WARNING**: This will overwrite your GitHub repository history. Make sure:
   - You have a backup (the script creates one)
   - No one else is actively using this repository
   - You're okay with losing the old git history

### Option 2: Remove Specific Files from History (Advanced)

This uses `git filter-branch` to remove specific files from all commits.

**Pros:**
- ✅ Preserves most of your git history
- ✅ Only removes the problematic files

**Cons:**
- ⚠️ More complex
- ⚠️ Still requires force push
- ⚠️ Can be slow for large repositories

**Steps:**

1. Remove files from all commits:
   ```bash
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch CONTAINER_EXPLANATION.md COSMOS_DB_SETUP.md WOHNTICKET_SETUP.md WOHNTICKET_DEBUG.md WOHNTICKET_STATUS.md COSMOS_DB_SETUP.md VIEW_DATA_IN_AZURE.md setup_cosmos.sh create_cosmos_containers.sh get_connection_string.sh" \
     --prune-empty --tag-name-filter cat -- --all
   ```

2. Clean up:
   ```bash
   rm -rf .git/refs/original/
   git reflog expire --expire=now --all
   git gc --prune=now --aggressive
   ```

3. Force push:
   ```bash
   git push -f origin main
   ```

### Option 3: Use BFG Repo-Cleaner (Fastest)

BFG is a faster alternative to `git filter-branch`.

**Steps:**

1. Install BFG (if not installed):
   ```bash
   # Download from: https://rtyley.github.io/bfg-repo-cleaner/
   # Or use: brew install bfg (on macOS)
   ```

2. Remove files:
   ```bash
   java -jar bfg.jar --delete-files "CONTAINER_EXPLANATION.md" "COSMOS_DB_SETUP.md" "WOHNTICKET_SETUP.md"
   ```

3. Clean up and push:
   ```bash
   git reflog expire --expire=now --all
   git gc --prune=now --aggressive
   git push -f origin main
   ```

## Recommended Approach

I recommend **Option 1 (Fresh Repository)** because:
- Your repository is relatively new
- You want a completely clean history
- It's the simplest and safest method
- You have a backup of the old repository

## After Cleaning History

Once you've cleaned the history:

1. **Verify on GitHub**: Check that the files are no longer visible in commit history
2. **Update collaborators**: If anyone else has cloned the repo, they'll need to:
   ```bash
   git fetch origin
   git reset --hard origin/main
   ```
3. **Keep the backup**: Don't delete the backup directory until you're sure everything works

## Files to Remove from History

Based on the commit you linked, these files should be removed:
- `CONTAINER_EXPLANATION.md` (contains: gewoscout-db-1, gewoscout-azurite, gewoscout-rg, gewoscout-cosmos, gewoscout-db)
- `COSMOS_DB_SETUP.md` (contains: gewoscout-rg, gewoscout-cosmos, gewoscout-db)
- `WOHNTICKET_SETUP.md`
- `WOHNTICKET_DEBUG.md`
- `WOHNTICKET_STATUS.md`
- `VIEW_DATA_IN_AZURE.md`
- `setup_cosmos.sh`
- `create_cosmos_containers.sh`
- `get_connection_string.sh`
- Any other files with "gewoscout" references

## Verification

After cleaning, verify with:
```bash
# Check current files
git ls-files | grep -i gewoscout

# Check history (should show nothing)
git log --all --full-history -- "*gewoscout*"

# Check file contents in history
git log --all --full-history -p -- "*CONTAINER_EXPLANATION*"
```
