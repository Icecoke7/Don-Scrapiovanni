# Local Setup Verification Guide

After publishing to GitHub, your local setup should still work perfectly! Here's how to verify and what to watch out for.

## ✅ Why Your Local Setup Still Works

1. **Your `.env` file is gitignored** - It was never committed to GitHub
2. **Your personal tokens stay on your machine** - They're in `.env`, which is private
3. **Docker Compose reads from `.env`** - Your containers will use your local values
4. **Code uses environment variables** - No hardcoded values, so it works with your `.env`

## 🔍 How to Verify Your Local Setup

### 1. Check Your .env File

```bash
# Verify .env exists and has your values
cat .env | grep TELEGRAM
# Should show your actual tokens (not empty)
```

### 2. Check Docker Containers

```bash
# Check if containers are running
docker ps | grep staatsoper

# Check container logs
docker logs staatsoper-scraper -f | grep -i staatsoper
```

### 3. Test the Scraper

```bash
# Restart containers to ensure they pick up environment variables
docker compose down
docker compose up -d

# Watch logs for the scraper
docker logs staatsoper-scraper -f | grep -i staatsoper
```

### 4. Verify Environment Variables in Container

```bash
# Check if environment variables are set in the container
docker exec staatsoper-scraper env | grep TELEGRAM
# Should show your actual values (not empty)
```

## ⚠️ What to Watch Out For

### 1. Never Commit Your .env File

**Always check before committing:**
```bash
git status
# Make sure .env is NOT listed!
```

If `.env` appears in `git status`, it means it's not properly gitignored. Check your `.gitignore` file.

### 2. Keep Your .env File Updated

If you change your Telegram token or chat ID:
1. Update `.env` file locally
2. Restart containers: `docker compose restart staatsoper-scraper`
3. **Never commit `.env` to git!**

### 3. Pulling Updates from GitHub

When you pull updates from GitHub:
```bash
git pull origin main
```

Your `.env` file will **not** be affected because it's gitignored. Your local tokens stay safe.

### 4. If You Clone the Repository Elsewhere

If you clone the repository on another machine:
1. Copy `.env.example` to `.env`
2. Fill in your own values
3. Your `.env` on the new machine will be different from your original one

## 🧪 Quick Test Commands

### Test 1: Verify .env is Protected
```bash
# This should return nothing (file is gitignored)
git ls-files | grep "\.env$"
```

### Test 2: Verify Containers Can Read Environment Variables
```bash
docker compose config | grep TELEGRAM
# Should show your values from .env (not empty defaults)
```

### Test 3: Test Telegram Connection
```bash
# Test if your Telegram bot works
curl -X POST "https://api.telegram.org/bot<YOUR_TOKEN>/getMe"
# Replace <YOUR_TOKEN> with your actual token from .env
```

### Test 4: Check Scraper is Running
```bash
# Wait for 09:30 AM Austria time, or check logs
docker logs staatsoper-scraper --since 1h | grep -i staatsoper
```

## 🔄 Workflow After Publishing

### Normal Daily Use:
1. Your scraper runs automatically at 09:30 AM
2. Your `.env` file stays on your machine
3. No changes needed!

### When You Update Code:
1. Make changes locally
2. Test locally: `docker compose restart staatsoper-scraper`
3. Commit and push: `git add . && git commit -m "..." && git push`
4. Your `.env` is never touched

### When You Pull Updates:
1. Pull from GitHub: `git pull origin main`
2. Your `.env` stays the same (it's gitignored)
3. Restart if needed: `docker compose restart staatsoper-scraper`

## 🚨 Red Flags - If Something Goes Wrong

### Problem: Scraper stops working after git pull
**Solution:** Your `.env` might have been overwritten. Check:
```bash
cat .env | grep TELEGRAM
# If empty, restore from backup or recreate
```

### Problem: "TELEGRAM_TOKEN not set" errors
**Solution:** 
1. Check `.env` exists: `test -f .env && echo "exists" || echo "missing"`
2. Check values: `cat .env | grep TELEGRAM`
3. Restart container: `docker compose restart staatsoper-scraper`

### Problem: Accidentally committed .env
**Solution:**
1. **Immediately revoke your tokens** (in Telegram, revoke the bot token)
2. Remove from git: `git rm --cached .env`
3. Add to `.gitignore` if not already there
4. Create new tokens and update `.env`
5. Commit the fix: `git commit -m "Remove .env from git"`

## 📋 Summary Checklist

- [ ] `.env` file exists locally
- [ ] `.env` contains your Telegram token and chat ID
- [ ] `.env` is in `.gitignore` (check with `git check-ignore .env`)
- [ ] Docker containers can read environment variables
- [ ] Scraper logs show no errors
- [ ] You never commit `.env` to git

## ✅ Your Setup is Safe!

Your local installation is completely independent from what's on GitHub:
- ✅ Your tokens are private (in `.env`, gitignored)
- ✅ Your code works locally (reads from `.env`)
- ✅ GitHub has no access to your tokens
- ✅ You can continue using your scraper normally

The only thing that changed is that your code is now public on GitHub. Your personal configuration stays private on your machine!
