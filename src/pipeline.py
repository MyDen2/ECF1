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

