import os
import re
import time
import hashlib
from urllib.parse import urljoin
from src.storage.minio_client import ensure_bucket, object_exists, upload_bytes


import requests
from bs4 import BeautifulSoup


BASE_URL = "https://books.toscrape.com/"
RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def _get_soup(session: requests.Session, url: str, delay_s: float, logger) -> BeautifulSoup:
    try:
        logger.info(f"GET {url}")
        resp = session.get(url, timeout=20)
        resp.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Erreur HTTP sur {url} : {e}")
        raise
    time.sleep(delay_s)
    return BeautifulSoup(resp.text, "lxml")

def _download_image(session, img_url, out_dir, logger):
   
    bucket = os.getenv("S3_BUCKET", "images")
    ensure_bucket(bucket)

    ext = os.path.splitext(img_url.split("?")[0])[1] or ".jpg"
    filename = hashlib.md5(img_url.encode("utf-8")).hexdigest() + ext

    prefix = (out_dir or "books").strip("/")

    key = f"{prefix}/{filename}"

    if object_exists(bucket, key):
        logger.debug(f"Image déjà présente dans MinIO : s3://{bucket}/{key}")
        return key

    try:
        r = session.get(img_url, timeout=30)
        r.raise_for_status()
        content_type = r.headers.get("Content-Type", "image/jpeg")
        upload_bytes(bucket=bucket, key=key, data=r.content, content_type=content_type)
        logger.info(f"Image uploadée dans MinIO : s3://{bucket}/{key}")
        return key
    except requests.RequestException as e:
        logger.warning(f"Impossible de télécharger l’image {img_url} : {e}")
        return None
    except Exception as e:
        logger.warning(f"Impossible d’uploader l’image vers MinIO {img_url} : {e}")
        return None


def scrape_books(
    user_agent,
    logger,
    delay_s=1.0,
    download_images=True,
    images_dir="books",
):
    logger.info("Début du scraping Books to Scrape")

    session = requests.Session()
    session.headers.update({"User-Agent": user_agent})

    home = _get_soup(session, BASE_URL, delay_s, logger)

    cat_links = home.select("div.side_categories ul li ul li a")
    categories = [(a.get_text(strip=True), urljoin(BASE_URL, a["href"])) for a in cat_links]

    rows = []

    for cat_name, cat_url in categories:
        logger.info(f"Catégorie : {cat_name}")
        next_url = cat_url

        while next_url:
            soup = _get_soup(session, next_url, delay_s, logger)

            books = soup.select("article.product_pod")
            logger.info(f"{len(books)} livres trouvés sur la page")

            for book in books:
                title = book.select_one("h3 a").get("title", "").strip()
                price_text = book.select_one("p.price_color").get_text(strip=True)
                rating_class = book.select_one("p.star-rating").get("class", [])
                rating_word = rating_class[1] if len(rating_class) > 1 else ""
                rating = RATING_MAP.get(rating_word, 0)

                availability_txt = book.select_one("p.instock.availability").get_text(" ", strip=True)
                in_stock = "In stock" in availability_txt

                img = book.select_one("div.image_container img")
                img_url = urljoin(BASE_URL, img.get("src")) if img else None
                img_path = None

                if download_images and img_url:
                    img_path = _download_image(session, img_url, images_dir, logger)

                rows.append(
                    {
                        "title": title,
                        "category": cat_name,
                        "price_raw": price_text,
                        "rating": rating,
                        "book_availability": in_stock,
                        "img_url": img_url,
                        "img_path": img_path,
                    }
                )

            next_a = soup.select_one("li.next a")
            next_url = urljoin(next_url, next_a["href"]) if next_a else None

    logger.info(f"Scraping terminé : {len(rows)} livres extraits")
    return rows
