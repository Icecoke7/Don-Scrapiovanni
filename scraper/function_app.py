import azure.functions as func

app = func.FunctionApp()

# Public scraper (on GitHub)
import scraper_staatsoper

# Local-only scrapers (not on GitHub, gitignored)
try:
    import scraper_bwsg
    app.register_functions(scraper_bwsg.bp)
except ImportError:
    pass

try:
    import scraper_wbv_gpa
    app.register_functions(scraper_wbv_gpa.bp)
except ImportError:
    pass

try:
    import scraper_oevw
    app.register_functions(scraper_oevw.bp)
except ImportError:
    pass

try:
    import scraper_wohnticket
    app.register_functions(scraper_wohnticket.bp)
except ImportError:
    pass

# Register public scraper (always available, on GitHub)
app.register_functions(scraper_staatsoper.bp)
