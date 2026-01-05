import os
import shutil


def copy_to_bronze(src_path: str, bronze_dir: str, run_id: str, dest_name: str) -> str:
    out_dir = os.path.join(bronze_dir, f"run_id={run_id}")
    os.makedirs(out_dir, exist_ok=True)

    if not os.path.exists(src_path):
        raise FileNotFoundError(f"Fichier source introuvable: {src_path}")

    dest_path = os.path.join(out_dir, dest_name)
    shutil.copy2(src_path, dest_path)

    if not os.path.exists(dest_path):
        raise RuntimeError(f"Copie échouée, fichier absent: {dest_path}")

    return dest_path
