def transform_quotes(raw_rows: list[dict], logger=None) -> list[dict]:
    clean = []
    seen = set()

    for r in raw_rows:
        text = (r.get("quote_text") or "").strip()
        author = (r.get("author") or "").strip()
        tags = r.get("tags") or []

        if not text or not author:
            continue

        key = (text, author)
        if key in seen:
            continue
        seen.add(key)

        clean.append(
            {
                "quote_text": text,
                "author": author,
                "tags": tags,
            }
        )

    if logger:
        logger.info(f"Transform Quotes: {len(clean)} lignes valides (sur {len(raw_rows)})")
    return clean
