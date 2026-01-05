from dotenv import load_dotenv
from src.pipeline import ECFPipeline
from src.utils.logger import setup_logger


def main():
    load_dotenv("config/.env")

    logger = setup_logger("ECF_PIPELINE", "logs/ecf_pipeline.log")

    config = {
        # Sources
        "partner_xlsx_path": "data/partenaire_librairies.xlsx",
        "api_adresse_url": "https://api-adresse.data.gouv.fr/search/",

        # Scraping
        "user_agent": "DataPulseAnalyticsBot/1.0",
        "scrape_delay_seconds": 1.0,
        "download_images": True,

        # Transform
        "gbp_to_eur": 1.17,

        # Output folders
        "bronze_dir": "data/bronze",
        "silver_dir": "data/silver",
    }

    pipeline = ECFPipeline(config=config, logger=logger)
    pipeline.run()


if __name__ == "__main__":
    main()
