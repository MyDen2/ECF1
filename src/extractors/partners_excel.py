import os
import pandas as pd

REQUIRED_COLUMNS = [
    "nom_librairie",
    "adresse",
    "code_postal",
    "ville",
    "contact_nom",
    "contact_email",
    "contact_telephone",
    "ca_annuel",
    "date_partenariat",
    "specialite",
]


def read_partners_excel(xlsx_path: str, logger) -> list[dict]:
    """
    Lecture + validation du fichier Excel partenaire.
    Retourne des dicts BRUTS (avec PII) -> Bronze.
    """
    if not os.path.exists(xlsx_path):
        raise FileNotFoundError(f"Excel introuvable: {xlsx_path}")

    logger.info(f"Lecture Excel partners: {xlsx_path}")
    df = pd.read_excel(xlsx_path, engine="openpyxl")

    # Validation colonnes
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Colonnes manquantes dans l'Excel: {missing}")

    logger.info(f"Colonnes OK ({len(df.columns)} colonnes)")
    logger.info(f"Lignes Excel: {len(df)}")

    # suppression des lignes complètement vides
    df = df.dropna(how="all")

    rows = df.to_dict(orient="records")
    logger.info(f"Rows prêtes: {len(rows)}")
    return rows
