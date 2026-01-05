# import csv
# import os


# def write_silver_csv(rows: list[dict], dataset: str, run_id: str, silver_dir: str) -> str:
#     out_dir = os.path.join(silver_dir, f"run_id={run_id}")
#     os.makedirs(out_dir, exist_ok=True)

#     path = os.path.join(out_dir, f"{dataset}_clean.csv")

#     headers = ["title", "category", "price", "rating", "book_availability", "img_url", "img_path"]
#     with open(path, "w", newline="", encoding="utf-8") as f:
#         writer = csv.DictWriter(f, fieldnames=headers)
#         writer.writeheader()
#         for r in rows:
#             writer.writerow({h: r.get(h) for h in headers})

#     return path

import csv
import os


def write_silver_csv(rows: list[dict], dataset: str, run_id: str, silver_dir: str) -> str:
    out_dir = os.path.join(silver_dir, f"run_id={run_id}")
    os.makedirs(out_dir, exist_ok=True)

    path = os.path.join(out_dir, f"{dataset}_clean.csv")

    if not rows:
        # crée un fichier vide (sans casser)
        with open(path, "w", newline="", encoding="utf-8") as f:
            f.write("")
        return path

    # colonnes = union des clés (stable)
    fieldnames = sorted({k for r in rows for k in r.keys()})

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    return path
