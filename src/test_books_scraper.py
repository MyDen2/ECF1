from utils.logger import setup_logger
from extractors.books_scraper import scrape_books

def main():
    logger = setup_logger("BOOKS_TEST", "logs/books_test.log")

    rows = scrape_books(
        user_agent="DataPulseAnalyticsBot/1.0",
        logger=logger,
        delay_s=1.0,              # politesse
        download_images=False     # d’abord on teste sans images (plus rapide)
    )

    print(f"✅ Livres extraits: {len(rows)}")
    print("Exemple (1er item):")
    print(rows[0] if rows else "Aucun résultat")
    print("rows[0].keys() : ", rows[0].keys())
    print("rows[0] : ", rows[0])


if __name__ == "__main__":
    main()
