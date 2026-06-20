import azure.functions as func

app = func.FunctionApp()

# Register only Staatsoper scraper
import scraper_staatsoper
app.register_functions(scraper_staatsoper.bp)
