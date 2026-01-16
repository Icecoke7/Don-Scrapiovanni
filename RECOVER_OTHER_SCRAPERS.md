# Recovering Other Scrapers for Local Use

The other scrapers (oevw, wbv_gpa, bwsg, wohnticket) were removed from the GitHub repository when we cleaned it up. However, they still exist in git history and can be recovered for local use.

## Current Situation

- **GitHub Repository (Don-Scrapiovanni)**: Only contains `scraper_staatsoper.py` (public)
- **Git History**: Other scrapers still exist and can be recovered
- **Your Local Setup**: Can use all scrapers locally if you recover them

## Option 1: Recover for Local Use Only (Recommended)

If you want to use the other scrapers locally but keep the GitHub repo clean:

### Step 1: Recover the scraper files

```bash
# Recover from git history (before cleanup commit)
git show a57d883^:scrapers/impl/scraper_oevw.py > scraper/scraper_oevw.py
git show a57d883^:scrapers/impl/scraper_wbv_gpa.py > scraper/scraper_wbv_gpa.py
git show a57d883^:scrapers/impl/scraper_bwsg.py > scraper/scraper_bwsg.py
git show a57d883^:scrapers/impl/scraper_wohnticket.py > scraper/scraper_wohnticket.py 2>/dev/null || echo "wohnticket might not exist in that commit"
```

### Step 2: Update function_app.py to register all scrapers

```python
import azure.functions as func

app = func.FunctionApp()

import scraper_staatsoper
import scraper_oevw
import scraper_wbv_gpa
import scraper_bwsg
# import scraper_wohnticket  # if you have it

app.register_functions(scraper_staatsoper.bp)
app.register_functions(scraper_oevw.bp)
app.register_functions(scraper_wbv_gpa.bp)
app.register_functions(scraper_bwsg.bp)
# app.register_functions(scraper_wohnticket.bp)  # if you have it
```

### Step 3: Add to .gitignore (so they're not committed)

```bash
# Add to .gitignore
echo "scraper/scraper_oevw.py" >> .gitignore
echo "scraper/scraper_wbv_gpa.py" >> .gitignore
echo "scraper/scraper_bwsg.py" >> .gitignore
echo "scraper/scraper_wohnticket.py" >> .gitignore
```

### Step 4: Rebuild and test

```bash
docker compose build
docker compose up -d
docker logs staatsoper-scraper -f
```

## Option 2: Add Them Back to GitHub

If you want the other scrapers in the public repository:

1. Recover the files (as above)
2. **Don't** add them to `.gitignore`
3. Commit and push them

**Note**: This will make all scrapers public on GitHub.

## Checking What Scrapers Were Available

To see all scrapers that existed before cleanup:

```bash
git show a57d883^:scrapers/function_app.py
```

This will show what was registered before.

## Important Notes

1. **Your `.env` file stays private** - It's gitignored, so your tokens are safe
2. **Local vs GitHub** - You can have different files locally than on GitHub
3. **Git history** - The old scrapers are always recoverable from git history

## Quick Recovery Script

I can create a script to recover all scrapers automatically. Would you like me to do that?
