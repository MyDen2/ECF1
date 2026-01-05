import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"


def _get_soup(session: requests.Session, url: str, delay_s: float, logger) -> BeautifulSoup:
    try:
        logger.info(f"GET {url}")
        resp = session.get(url, timeout=20)
        resp.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Erreur HTTP sur {url}: {e}")
        raise
    time.sleep(delay_s)
    return BeautifulSoup(resp.text, "lxml")


def scrape_quotes(user_agent: str, logger, delay_s: float = 1.0) -> list[dict]:
    """
    Pagination complète sur /page/1..n
    Sortie BRONZE : quote_text, author, tags (liste), source, page_url
    """
    session = requests.Session()
    session.headers.update({"User-Agent": user_agent})

    rows: list[dict] = []
    next_url = BASE_URL

    logger.info("Début scraping Quotes to Scrape")

    while next_url:
        soup = _get_soup(session, next_url, delay_s, logger)

        quote_blocks = soup.select("div.quote")
        logger.info(f"{len(quote_blocks)} quotes trouvées sur cette page")

        for q in quote_blocks:
            text = q.select_one("span.text").get_text(strip=True)
            author = q.select_one("small.author").get_text(strip=True)
            tags = [t.get_text(strip=True) for t in q.select("div.tags a.tag")]

            rows.append(
                {
                    "quote_text": text,
                    "author": author,
                    "tags": tags,
                    "source": "quotes.toscrape.com",
                    "page_url": next_url,
                }
            )

        next_a = soup.select_one("li.next a")
        next_url = urljoin(next_url, next_a["href"]) if next_a and next_a.get("href") else None

    logger.info(f"Fin scraping Quotes: {len(rows)} quotes extraites")
    return rows
