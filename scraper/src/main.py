import requests
from pathlib import Path

ROBOTS_URL = "https://books.toscrape.com/robots.txt"
USER_AGENT = (
    "FlyRankInternshipA9/1.0 (+https://github.com/primecodes-ops/polite-web-scraper)"
)
TIMEOUT_SECONDS = 10


# Check if robots.txt exists
def request_robots():
    try:
        r = requests.get(ROBOTS_URL)
    except requests.exceptions.RequestException as e:
        print(e)
        return f"Could not reach site: {e}"

    if r.status_code == 404:
        print("no robots file found")
        return "no robots file found"


# Download a catalogue page
def download_catalogue():
    PATH_URL = "https://books.toscrape.com/catalogue/page-1.html"
    CACHE_DIR = Path(__file__).resolve().parent.parent / "cache"
    CACHE_FILE = CACHE_DIR / "catalogue-page-1.html"

    if CACHE_FILE.exists():
        content = CACHE_FILE.read_bytes()
        print(f"CACHE HIT {len(content)} bytes")
        return content

    response = requests.get(
        PATH_URL, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT_SECONDS
    )

    if response.status_code != 200:
        raise RuntimeError(f"Fetch failed. Failed to get URL {response.status_code}")

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_bytes(response.content)
    print(f"FETCH {len(response.content)} bytes")
    return response.content


if __name__ == "__main__":
    # request_robots()
    download_catalogue()
