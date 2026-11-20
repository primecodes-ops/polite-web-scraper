import requests
import time
from datetime import datetime, timezone
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
    # make and name cache file
    file_category = url.split("/")[-2]
    file = url.split("/")[-1]

    if file == "":
        filename = file_category
    else:
        filename = f"{file_category}-{file}"

    CACHE_FILE = CACHE_DIR / filename

    # Use the cache parsed file
    if CACHE_FILE.exists():
        content = CACHE_FILE.read_bytes()
        print(f"CACHE HIT {filename} {len(content)} bytes")
        mtime = CACHE_FILE.stat().st_mtime
        fetched_at = datetime.fromtimestamp(mtime, timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        return content, False, fetched_at

    # request response and parse html
    response = requests.get(
        url, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT_SECONDS
    )
    # get time fetched request at
    fetched_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if response.status_code != 200:
        raise RuntimeError(f"Fetch failed. Failed to get URL {response.status_code}")

    # make directory for all cache files
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_bytes(response.content)
    print(f"FETCH {filename} {len(response.content)} bytes")

    return response.content, True, fetched_at


def parse_catalogue():
    pages_processed = 0
    current_page_url = f"{BASE_URL}catalogue/page-1.html"
    books_list = []
    books_dict = {}

    for _ in range(3):
        # Check if current URL cache exists, otherwise fetch
        # unpack content and if fetched succesfully
        content, was_fetched, _ = download_catalogue(current_page_url)

        # parse the content and store in soup
        soup = BeautifulSoup(content, "html.parser")

        # Add all books url to books_list
        books = soup.select(".product_pod > .image_container > a")

        # complete book URL
        for book in books:
            book_url = urljoin(current_page_url, book["href"])
            books_list.append(book_url)

            if book_url not in books_dict:
                books_dict[book_url] = current_page_url

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
    print(f"discovered={len(books_list)}")
    print(f"unique_urls={len(set(books_list))}")

    # key = product_url
    # value = source_page
    return books_dict


def get_text_tag(tag):
    return tag.get_text(strip=True) if tag is not None else None


def extract_record(product_url, source_page):
    content, was_fetched, fetched_at = download_catalogue(product_url)
    soup = BeautifulSoup(content, "html.parser")

    rating_tag = soup.select_one(".product_main > .star-rating")
    rating_text = rating_tag.get("class")[-1] if rating_tag is not None else None

    record = {
        "title": get_text_tag(soup.select_one(".product_main > h1")),
        "product_url": product_url,
        "price_text": get_text_tag(soup.select_one(".product_main > .price_color")),
        "availability_text": get_text_tag(
            soup.select_one(".product_main > .availability")
        ),
        "rating_text": rating_text,
        "description": get_text_tag(soup.select_one(".sub-header + p")),
        "source_page": source_page,
        "fetched_at": fetched_at,
    }

    if was_fetched:
        time.sleep(0.5)

    return record


def record_parsed_books(books_dict, limit=None):
    books_list = []

    for product_url, source_page in list(books_dict.items())[:limit]:
        record = extract_record(product_url, source_page)
        books_list.append(record)

    print(f"detail_pages={len(books_list)}")
    return books_list


if __name__ == "__main__":
    books_dict = parse_catalogue()
    books_list = record_parsed_books(books_dict)
    print(books_list[0])
