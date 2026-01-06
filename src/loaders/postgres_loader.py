import psycopg
from typing import List, Dict, Any

def load_books(conn: psycopg.Connection, books_rows: list[dict], truncate: bool = True) -> int:
    with conn.cursor() as cur:
        if truncate:
            cur.execute("TRUNCATE TABLE gold.books;")

        if not books_rows:
            return 0

        cur.executemany(
            """
            INSERT INTO gold.books (title, category, price, rating, book_availability, img_url, img_path)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            [
                (
                    r["title"],
                    r["category"],
                    r["price"],
                    r["rating"],
                    r["book_availability"],
                    r.get("img_url"),
                    r.get("img_path"),
                )
                for r in books_rows
            ],
        )

    return len(books_rows)

def load_quotes(conn: psycopg.Connection, quotes_rows: list[dict], truncate: bool = True) -> int:
    
    with conn.cursor() as cur:
        if truncate:
            cur.execute("TRUNCATE TABLE gold.quote_tags, gold.quotes, gold.authors RESTART IDENTITY;")

        if not quotes_rows:
            return 0

        # 1) Insert authors uniques
        authors = sorted({r["author"] for r in quotes_rows})
        cur.executemany(
            "INSERT INTO gold.authors (name) VALUES (%s) ON CONFLICT (name) DO NOTHING",
            [(a,) for a in authors],
        )

        # Map author -> author_id
        cur.execute("SELECT author_id, name FROM gold.authors")
        author_map = {name: author_id for author_id, name in cur.fetchall()}

        # 2) Insert quotes
        quote_values = [(r["quote_text"], author_map[r["author"]]) for r in quotes_rows]
        cur.executemany(
            "INSERT INTO gold.quotes (quote_text, author_id) VALUES (%s, %s)",
            quote_values,
        )

        # Map quote -> quote_id
        cur.execute(
            """
            SELECT q.quote_id, q.quote_text, a.name
            FROM gold.quotes q
            JOIN gold.authors a ON a.author_id = q.author_id
            """
        )
        quote_map = {(qt, an): qid for qid, qt, an in cur.fetchall()}

        # 3) Insert tags
        tag_rows = []
        for r in quotes_rows:
            qid = quote_map[(r["quote_text"], r["author"])]
            for tag in r.get("tags", []):
                tag_rows.append((qid, tag))

        if tag_rows:
            cur.executemany(
                "INSERT INTO gold.quote_tags (quote_id, tag) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                tag_rows,
            )

    return len(quotes_rows)

def load_partners(conn, rows: List[Dict[str, Any]], truncate: bool = False) -> int:
    """
    Charge les partners CLEAN (RGPD) dans gold.partners.
    rows attend des clés :
    nom_librairie, adresse, code_postal, ville, specialite, ca_annuel, date_partenariat, contact_hash
    """
    if not rows:
        return 0

    with conn.cursor() as cur:
        if truncate:
            cur.execute("TRUNCATE TABLE gold.partners RESTART IDENTITY CASCADE;")

        sql = """
        INSERT INTO gold.partners
          (nom_librairie, adresse, code_postal, ville, specialite, ca_annuel, date_partenariat, contact_hash)
        VALUES
          (%(nom_librairie)s, %(adresse)s, %(code_postal)s, %(ville)s, %(specialite)s,
           %(ca_annuel)s, %(date_partenariat)s, %(contact_hash)s)
        ON CONFLICT (nom_librairie, adresse, code_postal, ville)
        DO UPDATE SET
          specialite = EXCLUDED.specialite,
          ca_annuel = EXCLUDED.ca_annuel,
          date_partenariat = EXCLUDED.date_partenariat,
          contact_hash = EXCLUDED.contact_hash
        ;
        """
        cur.executemany(sql, rows)
        return cur.rowcount if cur.rowcount != -1 else len(rows)

def load_partner_geocoding(conn, rows, truncate=False):
    """
    rows: list[dict] avec partner_id, label, score, lon, lat
    """

    if not rows:
        return 0
    
    with conn.cursor() as cur:
        if truncate:
            cur.execute("TRUNCATE TABLE gold.partner_geocoding;")

        sql = """
        INSERT INTO gold.partner_geocoding (partner_id, label, score, longitude, latitude)
        VALUES (%(partner_id)s, %(label)s, %(score)s, %(lon)s, %(lat)s)
        ON CONFLICT (partner_id) DO UPDATE SET
          label = EXCLUDED.label,
          score = EXCLUDED.score,
          longitude = EXCLUDED.longitude,
          latitude = EXCLUDED.latitude;
        """

        cur.executemany(sql, rows)
        return cur.rowcount if cur.rowcount != -1 else len(rows)
