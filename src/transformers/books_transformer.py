import re


def _parse_gbp(price_raw: str) -> float:
    """
    Robust parsing: accepte '£45.17', 'Â£45.17', etc.
    On extrait juste le nombre.
    """
    if not price_raw:
        return 0.0
    # capture la première valeur du type 45.17
    m = re.search(r"(\d+(?:\.\d+)?)", price_raw.replace(",", "."))
    return float(m.group(1)) if m else 0.0


def transform_books(raw_rows: list[dict], gbp_to_eur: float, logger=None) -> list[dict]:
    out: list[dict] = []

    for r in raw_rows:
        title = (r.get("title") or "").strip()
        category = (r.get("category") or "").strip()
        rating = int(r.get("rating") or 0)
        availability = bool(r.get("book_availability"))

        if not title or not category:
            continue
        if rating < 1 or rating > 5:
            continue

        gbp = _parse_gbp(r.get("price_raw", ""))
        eur = round(gbp * gbp_to_eur, 2)
        if eur <= 0:
            continue

        out.append(
            {
                "title": title,
                "category": category,
                "price": eur,
                "rating": rating,
                "book_availability": availability,
                "img_url": r.get("img_url"),
                "img_path": r.get("img_path"),
            }
        )

    if logger:
        logger.info(f"Transform Books: {len(out)} lignes valides (sur {len(raw_rows)})")
    return out
