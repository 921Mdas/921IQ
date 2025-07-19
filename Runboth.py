import subprocess

# Start FastAPI backend with uvicorn
backend = subprocess.Popen(["uvicorn", "Main:app", "--reload"])

# Start scrapers (Main.py, assuming it doesn't contain the FastAPI app anymore)
scraper = subprocess.Popen(["python3", "Main.py"])

# Optional: start frontend dev server (if `app.py` is your frontend or Node dev server)
frontend = subprocess.Popen(["python3", "app.py"])

# Wait for processes to finish
backend.wait()
scraper.wait()
frontend.wait()
