import arxiv
import os
from pathlib import Path
import time

# ========== CONFIG ==========
SEARCH_QUERY = "physics"  # Change this if you want a more specific subfield
MAX_RESULTS = 1000
SAVE_DIR = "./arxiv_physics_papers"
REQUEST_DELAY = 3.0  # in seconds, to be nice to arXiv servers
# ============================

# Create the directory to store papers
Path(SAVE_DIR).mkdir(parents=True, exist_ok=True)

# Setup custom client with large page size and retry logic
client = arxiv.Client(
    page_size=100,
    delay_seconds=REQUEST_DELAY,
    num_retries=5
)

# Configure search
search = arxiv.Search(
    query=SEARCH_QUERY,
    max_results=MAX_RESULTS,
    sort_by=arxiv.SortCriterion.SubmittedDate
)

print(f"Fetching up to {MAX_RESULTS} physics papers...")
count = 0

for result in client.results(search):
    count += 1
    print(f"[{count}/{MAX_RESULTS}] Downloading: {result.title}")
    try:
        # Safe filename generation
        filename = f"{result.entry_id.split('/')[-1]}.pdf"
        result.download_pdf(dirpath=SAVE_DIR, filename=filename)
    except Exception as e:
        print(f"Failed to download {result.title}: {e}")

    if count >= MAX_RESULTS:
        break

print("Done downloading papers.")
