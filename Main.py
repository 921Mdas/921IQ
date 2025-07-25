# === Standard Library ===
import os
import logging

# === Third-Party Libraries ===
import uvicorn
import spacy
import wikipedia
from dotenv import load_dotenv
from keybert import KeyBERT
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from playwright.sync_api import sync_playwright

# === Local Modules ===
from routes.health import router as health_router
from routes.data import router as getData_router
# from routes.entity import router as getEntities_router
# from routes.summary import router as getSummary_router
from auth_routes import router as auth_router
from NewsScrapers.DRCongo.Actucd import ActuCdScrap

# === Logging Configuration ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# === Load Environment Variables Safely ===
try:
    load_dotenv()
    if not os.getenv("MODE"):
        logger.warning("⚠️  .env loaded, but 'MODE' not set.")
except Exception as e:
    logger.error("❌ Failed to load .env file!", exc_info=e)

# === Init FastAPI App ===
app = FastAPI()

# === Routers ===
app.include_router(health_router)
app.include_router(getData_router)
# app.include_router(getEntities_router)
# app.include_router(getSummary_router)
app.include_router(auth_router, prefix="/auth")

# === CORS Setup ===
mode = os.getenv("MODE", "development")
origins = (
    [os.getenv("PRODUCTION_DOMAIN")] if mode == "production"
    else ["http://localhost:5173", "http://127.0.0.1:5173"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === AI + NLP Models ===
kw_model = KeyBERT()
nlp = spacy.load("en_core_web_sm")

# === Background Scraper Task ===
def run_scrapers():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            ActuCdScrap(page)
            browser.close()
        logger.info("✅ Scraping completed.")
    except Exception as e:
        logger.error("❌ Scraping failed due to browser error", exc_info=e)

# === Scrape-on-Demand Endpoint (Optional) ===
@app.post("/scrape")
async def trigger_scraping(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_scrapers)
    return {"message": "Scraping started in the background."}

# === Main Entry Point ===
if __name__ == "__main__":
    print("🚀 Starting server with uvicorn...")
    uvicorn.run("Main:app", host="0.0.0.0", port=5000, reload=True)
