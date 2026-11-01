# Polite Web Scraper

## Target Classification
- **Site:** [Books to scrape](https://books.toscrape.com), a practice website that is part of toscrape.com sandbox
- **Why:** The site is a sandbox that is free to experiment for those just starting out in making a web scraper, and is the ideal website to test the assignment on.
- **How Much:** The first 3 catalogue pages only, which lead to 60 book pages. Nothing else on the site is requested.
- **Data collected:** For each book: title, product URL, price text, availability text, rating text, description (null if missing), the catalogue page it came from, and the fetch time. A numeric `price_gbp` is derived from the price text. No personal data is involved.
- **robots.txt check:** I requested https://books.toscrape.com/robots.txt once. The response was a client error (4xx), so the result is: **no robots file found**. A missing file is not permission; the permission here comes from the site being a purpose-built practice sandbox.
- **Why this is appropriate:** The site is a public sandbox built for scraping practice, and the scope is small, slow and limited to public pages.

I will not reuse this code on another site without checking its rules and terms first.