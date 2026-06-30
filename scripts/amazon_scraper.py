import os
from typing import List, Optional
from urllib.parse import urljoin

import pandas as pd
from playwright.sync_api import Locator, Page, sync_playwright


def _safe_text(locator: Locator, fallback: Optional[str] = None) -> Optional[str]:
    try:
        text = locator.first.inner_text(timeout=5000).strip()
        return text or fallback
    except Exception:
        return fallback


def _safe_attr(locator: Locator, name: str, fallback: Optional[str] = None) -> Optional[str]:
    try:
        value = locator.first.get_attribute(name, timeout=5000)
        return value or fallback
    except Exception:
        return fallback


def extract_amazon_search_results(page: Page, product_url: str, max_results: int = 10) -> List[dict]:
    page.goto(product_url, wait_until="domcontentloaded", timeout=120000)
    page.wait_for_timeout(4000)

    try:
        page.get_by_role("button", name="Accept All").click(timeout=5000)
    except Exception:
        pass

    page.wait_for_selector("div[data-component-type='s-search-result']", timeout=30000)
    search_items = page.locator("div[data-component-type='s-search-result']")
    results = []

    for index in range(min(search_items.count(), max_results)):
        item = search_items.nth(index)
        title = _safe_text(item.locator("h2 span"))
        url = None

        relative_url = _safe_attr(item.locator("div[data-cy='title-recipe'] a"), "href")
        if relative_url and not relative_url.startswith("javascript:"):
            url = urljoin("https://www.amazon.com", relative_url)

        price = _safe_text(item.locator(".a-price .a-offscreen"))
        if not price:
            price = _safe_text(item.locator(".s-price .a-offscreen"))

        if title or price or url:
            results.append({
                "title": title,
                "url": url,
                "price": price,
            })

    return results


def main() -> None:
    product_url = os.getenv(
        "AMAZON_PRODUCT_URL",
        "https://www.amazon.com/s?k=databricks+books",
    )
    max_results = int(os.getenv("AMAZON_MAX_RESULTS", "10"))

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1440, "height": 1400},
            locale="en-US",
        )
        page = context.new_page()
        results = extract_amazon_search_results(page, product_url, max_results=max_results)
        context.close()
        browser.close()

    df = pd.DataFrame(results)
    output_file = os.getenv("AMAZON_CSV_OUTPUT", "amazon_databricks_books.csv")
    df.to_csv(output_file, index=False)
    print(f"Saved {len(df)} records to {output_file}")


if __name__ == "__main__":
    main()
