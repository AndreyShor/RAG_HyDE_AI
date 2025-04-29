import arxiv
import os
from pathlib import Path
from tqdm import tqdm
import time

# All official arXiv physics categories
PHYSICS_CATEGORIES = [
    "physics.acc-ph", "physics.app-ph", "physics.ao-ph", "physics.atom-ph",
    "physics.atm-clus", "physics.bio-ph", "physics.chem-ph", "physics.class-ph",
    "physics.comp-ph", "physics.data-an", "physics.flu-dyn", "physics.gen-ph",
    "physics.geo-ph", "physics.hist-ph", "physics.ins-det", "physics.med-ph",
    "physics.optics", "physics.ed-ph", "physics.soc-ph", "physics.plasm-ph",
    "physics.pop-ph", "physics.space-ph"
]

BASE_SAVE_DIR = Path("./all_physics_papers")
MAX_RESULTS_PER_CATEGORY = 1000
PAGE_SIZE = 100
DELAY_SECONDS = 3.0

client = arxiv.Client(
    page_size=PAGE_SIZE,
    delay_seconds=DELAY_SECONDS,
    num_retries=3
)

for category in PHYSICS_CATEGORIES:
    category_dir = BASE_SAVE_DIR / category
    category_dir.mkdir(parents=True, exist_ok=True)

    print(f"🔍 Searching in {category}")
    search = arxiv.Search(
        query=f"cat:{category}",
        max_results=MAX_RESULTS_PER_CATEGORY,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )

    for result in tqdm(client.results(search), desc=f"Downloading {category}", leave=False):
        paper_id = result.entry_id.split("/")[-1]
        filename = category_dir / f"{paper_id}.pdf"
        if filename.exists():
            continue  # Skip already downloaded

        try:
            result.download_pdf(dirpath=category_dir, filename=filename.name) # type: ignore
        except Exception as e:
            print(f"❌ Failed to download {paper_id}: {e}")
        time.sleep(1)
