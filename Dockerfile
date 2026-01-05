FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code
COPY src ./src

# Créer les dossiers montés en volumes (sécurité)
RUN mkdir -p /app/data /app/logs

# Lancer le pipeline
CMD ["python", "-m", "src.main"]
