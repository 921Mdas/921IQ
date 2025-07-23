# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from auth_routes import router as auth_router
# from NewsScrapers.DRCongo.Actucd import ActuCdScrap
# from playwright.sync_api import sync_playwright

# app = FastAPI()

# # ✅ Add this CORS middleware setup
# origins = [
#     "http://localhost:5173",
#     "http://127.0.0.1:5173"
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,  # or ["*"] for testing only
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ✅ Register your /auth routes
# app.include_router(auth_router, prefix="/auth")

# # ✅ Your scraping logic (unchanged)
# def run_scrapers():
#     try:
#         with sync_playwright() as p:
#             browser = p.chromium.launch(headless=True)
#             context = browser.new_context()
#             page = context.new_page()
#             ActuCdScrap(page)
#             browser.close()
#     except Exception as e:
#         print('❌ Browser error:', e)
#     finally:
#         print('✅ Done')

# if __name__ == "__main__":
#     run_scrapers()


import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth_routes import router as auth_router
from NewsScrapers.DRCongo.Actucd import ActuCdScrap
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

mode = os.getenv("MODE")

origins = (
    [os.getenv('PRODUCTION_DOMAIN')]  # 🔁 Replace with actual production domain
    if mode == "production"
    else [
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth")

def run_scrapers():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            ActuCdScrap(page)
            browser.close()
    except Exception as e:
        print('❌ Browser error:', e)
    finally:
        print('✅ Done')

if __name__ == "__main__":
    run_scrapers()
