import os
import hashlib


def _hash_contact(nom: str, email: str, tel: str, salt: str) -> str:
    raw = f"{nom}|{email}|{tel}|{salt}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def transform_partners_rgpd(rows: list[dict], logger) -> list[dict]:
    salt = os.getenv("PII_SALT", "change_me")

    clean = []
    for r in rows:
        nom_lib = (r.get("nom_librairie") or "").strip()
        adresse = (r.get("adresse") or "").strip()

        if not nom_lib or not adresse:
            continue

        contact_hash = _hash_contact(
            (r.get("contact_nom") or "").strip(),
            (r.get("contact_email") or "").strip(),
            (str(r.get("contact_telephone") or "").strip()),
            salt,
        )

        clean.append({
            "nom_librairie": nom_lib,
            "adresse": adresse,
            "code_postal": str(r.get("code_postal") or "").strip() or None,
            "ville": (r.get("ville") or "").strip() or None,
            "specialite": (r.get("specialite") or "").strip() or None,
            "ca_annuel": r.get("ca_annuel"),
            "date_partenariat": r.get("date_partenariat"),
            "contact_hash": contact_hash,
        })

    logger.info(f"Transform Partners (RGPD): {len(clean)} lignes valides (sur {len(rows)})")
    return clean
