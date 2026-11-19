import requests
import time
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Robots
ROBOTS_URL = "https://books.toscrape.com/robots.txt"
BASE_URL = "https://books.toscrape.com/"

# catalogues
USER_AGENT = (
    "FlyRankInternshipA9/1.0 (+https://github.com/primecodes-ops/polite-web-scraper)"
)
TIMEOUT_SECONDS = 10
CACHE_DIR = Path(__file__).resolve().parent.parent / "cache"


# Check if robots.txt exists
def request_robots():
    try:
        page = requests.get(ROBOTS_URL)
    except requests.exceptions.RequestException as e:
        print(e)
        return f"Could not reach site: {e}"

    if page.status_code == 404:
        print("no robots file found")
        return "no robots file found"


# Download a catalogue page
def download_catalogue(url):
    # Cache file naming
    file_category = url.split("/")[-2]
    file = url.split("/")[-1]

    if file == "":
        filename = file_category
    else:
        filename = f"{file_category}-{file}"

    CACHE_FILE = CACHE_DIR / filename

    if CACHE_FILE.exists():
        content = CACHE_FILE.read_bytes()
        print(f"CACHE HIT {filename} {len(content)} bytes")
        return content, False

    response = requests.get(
        url, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT_SECONDS
    )

    if response.status_code != 200:
        raise RuntimeError(f"Fetch failed. Failed to get URL {response.status_code}")

    # parse to cache HTML
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_bytes(response.content)
    print(f"FETCH {filename} {len(response.content)} bytes")
    return response.content, True


def parse_catalogue():
    catalogue_pages = 1
    pages_processed = 0
    current_page_url = f"{BASE_URL}catalogue/page-{catalogue_pages}.html"
    books_cont = []

    for _ in range(3):
        # Check if current URL cache exists, otherwise fetch
        # unpack content and if fetched succesfully
        content, was_fetched = download_catalogue(current_page_url)

        # parse the content and store in soup
        soup = BeautifulSoup(content, "html.parser")

        # Add all books url to books_cont
        books = soup.select(".product_pod > .image_container > a")

        # complete book URL
        for book in books:
            book_url = urljoin(current_page_url, book["href"])
            books_cont.append(book_url)

        # get URL of next page
        next_page = soup.select_one("div > .pager > .next > a")
        pages_processed += 1

        if next_page is None:
            print("No pages left to parse.")
            break

        next_page_url = urljoin(f"{BASE_URL}catalogue/", next_page["href"])

        if was_fetched:
            time.sleep(0.5)

        current_page_url = next_page_url

    print(f"catalogue_pages={pages_processed}")
    print(f"discovered={len(books_cont)}")
    print(f"unique_urls={len(set(books_cont))}")


if __name__ == "__main__":
    parse_catalogue()
