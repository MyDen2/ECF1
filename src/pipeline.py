import os
from datetime import datetime, timezone

import psycopg

from src.extractors.books_scraper import scrape_books
from src.transformers.books_transformer import transform_books
from src.extractors.quotes_scraper import scrape_quotes
from src.transformers.quotes_transformer import transform_quotes
from src.loaders.bronze_writer import write_bronze_json
from src.loaders.silver_writer import write_silver_csv
from src.loaders.postgres_loader import load_books, load_quotes
from src.loaders.bronze_files import copy_to_bronze
from src.extractors.partners_excel import read_partners_excel
from src.transformers.partners_cleaner import transform_partners_rgpd
from src.loaders.postgres_loader import load_partners
from src.extractors.adresse_api import geocode_address
from src.loaders.postgres_loader import load_partner_geocoding

class ECFPipeline:
    def __init__(self, config: dict, logger):
        self.config = config
        self.logger = logger

    def run(self):
        run_id = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")

        self.logger.info("=" * 60)
        self.logger.info(f"START ECF PIPELINE run_id={run_id}")
        self.logger.info("=" * 60)

        try:
            # Partners Excel (Bronze snapshot + lecture/validation)
            self._bronze_snapshot_partners_excel(run_id)
            partners_raw = self._read_partners_excel_bronze(run_id)
            self.logger.info(f"Partners RAW (Excel) count = {len(partners_raw)}")

            # Nettoyage et mise en ^place RGPD (Silver)
            partners_clean = self._transform_partners(partners_raw, run_id)
            self.logger.info(f"Partners CLEAN (RGPD) count = {len(partners_clean)}")

            # Envoi partners dans la BDD (gold) 
            self._load_partners(partners_clean, run_id)

            # 2) Partners -> geocoding -> load geocoding
            self._geocode_partners(run_id)

            # Books
            raw = self._extract_books(run_id)
            clean = self._transform_books(raw, run_id)
            self._load_books(clean, run_id)

            # Quotes
            raw_quotes = self._extract_quotes(run_id)
            clean_quotes = self._transform_quotes(raw_quotes, run_id)
            self._load_quotes(clean_quotes, run_id)

            self.logger.info("PIPELINE TERMINÉ AVEC SUCCÈS ✅")

        except Exception as e:
            self.logger.exception(f"PIPELINE EN ERREUR ❌ : {e}")
            raise

    def _bronze_snapshot_partners_excel(self, run_id: str) -> str:
        self.logger.info("[BRONZE] Snapshot Excel partenaires")

        src = self.config["partner_xlsx_path"]
        dest = copy_to_bronze(
            src_path=src,
            bronze_dir=self.config["bronze_dir"],
            run_id=run_id,
            dest_name="partners_source.xlsx",
        )

        self.logger.info(f"Excel copié en Bronze: {dest}")
        return dest

    def _read_partners_excel_bronze(self, run_id: str) -> list[dict]:
        self.logger.info("[EXTRACT] Lecture Excel partenaires (depuis Bronze)")

        # Chemin du snapshot Bronze
        bronze_xlsx = f"{self.config['bronze_dir']}/run_id={run_id}/partners_source.xlsx"

        rows = read_partners_excel(bronze_xlsx, logger=self.logger)

        return rows

    def _transform_partners(self, partners_raw: list[dict], run_id: str) -> list[dict]:
        self.logger.info("[2/3] TRANSFORMATION - Partners (RGPD)")
        clean = transform_partners_rgpd(partners_raw, logger=self.logger)
        silver_path = write_silver_csv(clean, "partners_clean", run_id, silver_dir=self.config["silver_dir"])
        self.logger.info(f"Silver écrit: {silver_path}")
        return clean

    def _load_partners(self, clean_rows, run_id: str):
        self.logger.info("[3/3] LOAD - PostgreSQL (gold.partners)")

        conn = psycopg.connect(
            dbname=os.getenv("DB_NAME", "db_ecf1"),
            user=os.getenv("DB_USER", "admin"),
            password=os.getenv("DB_PASSWORD", "admin"),
            host=os.getenv("DB_HOST", "db"),
            port=int(os.getenv("DB_PORT", "5432")),
        )
        conn.autocommit = True

        try:
            inserted = load_partners(conn, clean_rows, truncate=True)
            self.logger.info(f"Gold chargé: {inserted} lignes dans gold.partners")
        finally:
            conn.close() 

    def _extract_partners_for_geocoding(self, conn):
        with conn.cursor() as cur:
            cur.execute("""
                SELECT partner_id, adresse, code_postal, ville
                FROM gold.partners
                ORDER BY partner_id
            """)
            return cur.fetchall()

    def _extract_books(self, run_id: str) -> list[dict]:
        self.logger.info("[1/3] EXTRACTION - Books")

        rows = scrape_books(
            user_agent=self.config["user_agent"],
            logger=self.logger,
            delay_s=self.config["scrape_delay_seconds"],
            download_images=self.config["download_images"],
            images_dir=self.config.get("images_dir", "data/images/books"),
        )

        bronze_path = write_bronze_json(rows, "books", run_id, bronze_dir=self.config["bronze_dir"])
        self.logger.info(f"Bronze écrit: {bronze_path}")
        return rows

    def _transform_books(self, raw_rows: list[dict], run_id: str) -> list[dict]:
        self.logger.info("[2/3] TRANSFORMATION - Books")

        clean = transform_books(raw_rows, gbp_to_eur=self.config["gbp_to_eur"], logger=self.logger)

        silver_path = write_silver_csv(clean, "books", run_id, silver_dir=self.config["silver_dir"])
        self.logger.info(f"Silver écrit: {silver_path}")
        return clean

    def _load_books(self, clean_rows: list[dict], run_id: str) -> None:
        self.logger.info("[3/3] LOAD - PostgreSQL (gold.books)")

        conn = psycopg.connect(
            dbname=os.getenv("DB_NAME", "db_ecf1"),
            user=os.getenv("DB_USER", "admin"),
            password=os.getenv("DB_PASSWORD", "admin"),
            host=os.getenv("DB_HOST", "db"),
            port=int(os.getenv("DB_PORT", "5432")),
        )
        conn.autocommit = True

        inserted = load_books(conn, clean_rows, truncate=True)
        conn.close()

        self.logger.info(f"Gold chargé: {inserted} lignes dans gold.books")

    def _extract_quotes(self, run_id: str) -> list[dict]:
        self.logger.info("[1/3] EXTRACTION - Quotes")
        rows = scrape_quotes(
            user_agent=self.config["user_agent"],
            logger=self.logger,
            delay_s=self.config["scrape_delay_seconds"],
        )
        bronze_path = write_bronze_json(rows, "quotes", run_id, bronze_dir=self.config["bronze_dir"])
        self.logger.info(f"Bronze écrit: {bronze_path}")
        return rows

    def _transform_quotes(self, raw_rows: list[dict], run_id: str) -> list[dict]:
        self.logger.info("[2/3] TRANSFORMATION - Quotes")
        clean = transform_quotes(raw_rows, logger=self.logger)

        # écrire un silver "aplati" (tags en texte)
        flat = [{**r, "tags": ",".join(r.get("tags", []))} for r in clean]
        silver_path = write_silver_csv(flat, "quotes", run_id, silver_dir=self.config["silver_dir"])
        self.logger.info(f"Silver écrit: {silver_path}")
        return clean

    def _load_quotes(self, clean_rows: list[dict], run_id: str) -> None:
        self.logger.info("[3/3] LOAD - PostgreSQL (quotes)")
        conn = psycopg.connect(
            dbname=os.getenv("DB_NAME", "db_ecf1"),
            user=os.getenv("DB_USER", "admin"),
            password=os.getenv("DB_PASSWORD", "admin"),
            host=os.getenv("DB_HOST", "db"),
            port=int(os.getenv("DB_PORT", "5432")),
        )
        conn.autocommit = True
        inserted = load_quotes(conn, clean_rows, truncate=True)
        conn.close()
        self.logger.info(f"Gold chargé: {inserted} quotes")

    def _geocode_partners(self, run_id: str):
        self.logger.info("[API] Géocodage partenaires (API Adresse)")
        self.logger.info(f"Run Id : {run_id}")

        conn = psycopg.connect(
            dbname=os.getenv("DB_NAME", "db_ecf1"),
            user=os.getenv("DB_USER", "admin"),
            password=os.getenv("DB_PASSWORD", "admin"),
            host=os.getenv("DB_HOST", "db"),
            port=int(os.getenv("DB_PORT", "5432")),
        )
        conn.autocommit = True

        try:
            partners = self._extract_partners_for_geocoding(conn)
            if not partners:
                self.logger.warning("Aucun partner à géocoder (table gold.partners vide)")
                return

            out = []

            for (partner_id, adresse, code_postal, ville) in partners:
                q = f"{adresse} {code_postal or ''} {ville or ''}".strip()

                try:
                    geo = geocode_address(
                        query=q,
                        user_agent=self.config.get("user_agent", "DataPulseAnalyticsBot/1.0"),
                        delay_s=0.2,
                    )
                    if geo:
                        out.append({
                            "partner_id": partner_id,
                            "label": geo["label"],
                            "score": geo["score"],
                            "lon": geo["lon"],
                            "lat": geo["lat"],
                        })
                    else:
                        self.logger.warning(f"Adresse non trouvée: partner_id={partner_id} q='{q}'")
                except Exception as e:
                    self.logger.warning(f"Erreur géocodage partner_id={partner_id}: {e}")

            self.logger.info(f"Géocodage OK: {len(out)}/{len(partners)}")
            inserted = load_partner_geocoding(conn, out, truncate=False)
            self.logger.info(f"Gold chargé: {inserted} lignes dans gold.partner_geocoding")

        finally:
            conn.close()