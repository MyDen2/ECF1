from utils.logger import setup_logger
from extractors.quotes_scraper import scrape_quotes


def main():
    logger = setup_logger("QUOTES_TEST", "logs/quotes_test.log")

    rows = scrape_quotes(
        user_agent="DataPulseAnalyticsBot/1.0",
        logger=logger,
        delay_s=1.0,
    )

    print(f"✅ Quotes extraites: {len(rows)}")

    if rows:
        print("\nExemple (1ère quote):")
        print(rows[0])


if __name__ == "__main__":
    main()

