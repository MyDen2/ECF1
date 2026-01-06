# ECF1 – Plateforme Data Engineering & Analytics

## 📌 Présentation du projet

Ce projet consiste à concevoir et implémenter une **plateforme de traitement de données complète**, depuis la collecte de données hétérogènes jusqu’à leur exploitation analytique, en respectant les bonnes pratiques de **Data Engineering**, de **traçabilité**, et de **conformité RGPD**.

La plateforme intègre :
- des données issues de **scraping web**
- des données **Excel partenaires**
- une **API externe** de géocodage
- un stockage relationnel analytique
- un stockage objet pour les fichiers volumineux (images)

---

## 🏗️ Architecture globale

L’architecture repose sur un modèle **Lakehouse** structuré en couches :

- **Bronze** : données brutes, historisées, immuables
- **Silver** : données nettoyées, normalisées, conformes RGPD
- **Gold** : données prêtes à l’analyse dans PostgreSQL
- **Object Storage** : images stockées dans MinIO (S3 compatible)

Les traitements sont orchestrés par un **pipeline Python conteneurisé avec Docker**.

---

## 🧱 Technologies utilisées

| Usage | Technologie | Justification |
|-----|-----------|--------------|
| Orchestration | Python | Lisibilité, écosystème data mature |
| Scraping | Requests, BeautifulSoup | Léger et contrôlé |
| Stockage brut | Fichiers (JSON, XLSX) | Traçabilité et audit |
| Transformation | Pandas | Validation et nettoyage |
| Base analytique | PostgreSQL 16 | SQL standard, contraintes fortes |
| Object storage | MinIO | Stockage scalable des images |
| Conteneurisation | Docker / Docker Compose | Reproductibilité |
| Logging | logging (Python) | Observabilité du pipeline |

---

## 📂 Organisation du projet

```text
ECF1/
├── config/
│   ├── .env
│   └── config.yaml
|
├── data/
│   ├── bronze/
│   │   └── run_id=YYYY-MM-DDTHH-MM-SS/
│   |── silver/
│   |   └── run_id=YYYY-MM-DDTHH-MM-SS/
│   └── partenaire_librairies.xlsx
|
├── docs/
│   ├── DAT.md                    # Dossier Architecture Technique
│   └── RGPD_CONFORMITE.md        # Conformité RGPD
|
├── src/
│   ├── extractors/
│   |   ├── adresse_api.py                    
|   |   ├── book_scraper.py
|   |   ├── partners_excel.py
│   |   └── quotes_scraper.py        
│   ├── loaders/
│   |   ├── bronze_files.py                    
|   |   ├── bronze_writer.py
|   |   ├── postgres_loader.py
│   |   └── silver_writer.py
│   ├── transformers/
│   |   ├── books_transformer.py                    
|   |   ├── partners_cleaner.py
│   |   └── quotes_transformer.py
│   ├── storage/                    
│   |   └── minio_client.py 
│   ├── utils/                    
│   |   └── logger.py
│   ├── main.py
│   └── pipeline.py
│
├── sql/
│   ├── schema.sql
│   └── analyses.sql
│
├── logs/
│
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── README.md
├── ECF-DataPulse-MultiSources.md
└── requirements.txt

```

⚠️ Le dossier data/gold n’existe pas :
la couche Gold correspond à la base PostgreSQL, pas à des fichiers.

## 🔄 Pipeline de traitement

Chaque exécution du pipeline suit les étapes suivantes :

### 1️⃣ Snapshot Bronze
- Copie horodatée des sources (Excel partenaires, scraping web)
- Conservation des données brutes à des fins de traçabilité et d’audit

### 2️⃣ Extraction
- Lecture des données depuis la couche **Bronze**
- Aucune modification des données sources

### 3️⃣ Transformation (Silver)
- Nettoyage des données
- Typage et normalisation
- Application des règles de conformité **RGPD**

### 4️⃣ Chargement (Gold)
- Insertion des données dans **PostgreSQL**
- Application de contraintes d’intégrité (clés primaires, clés étrangères, unicité)

### 5️⃣ Enrichissement
- Géocodage des partenaires via une **API externe**
- Stockage des résultats dans des tables dédiées

### 6️⃣ Stockage des images
- Upload des images vers **MinIO** (Object Storage compatible S3)
- Stockage **uniquement de l’URL** de l’image en base de données

Chaque exécution du pipeline est identifiée par un **`run_id`**, garantissant une **traçabilité complète** de bout en bout.

---

## 🪵 Logging & traçabilité

Le projet intègre un système de **logging structuré** afin d’assurer la traçabilité complète des traitements et de faciliter le diagnostic en cas d’erreur.

### Objectifs du logging

- Suivi des exécutions du pipeline
- Identification rapide des erreurs ou blocages
- Audit des opérations réalisées (scraping, transformation, chargement)
- Analyse des performances et des volumes traités

### Organisation des logs

Les logs sont écrits dans le dossier : /logs

Chaque exécution du pipeline génère des messages horodatés indiquant :

- le `run_id` de l’exécution
- le démarrage et la fin de chaque étape
- les volumes de données traités
- les appels aux API externes
- les erreurs ou avertissements éventuels

### Niveaux de logs utilisés

- `INFO` : suivi normal du pipeline
- `WARNING` : anomalie non bloquante (ex. adresse non géocodable)
- `ERROR` : erreur bloquante entraînant l’arrêt du pipeline

Ce mécanisme garantit une **observabilité complète** du système, indispensable dans un contexte de production ou d’audit.

---

## 🔐 Conformité RGPD

Le projet intègre la conformité RGPD dès la conception :

- Identification explicite des données personnelles
- Pseudonymisation des données sensibles (hash des contacts)
- Séparation claire entre données sensibles et données analytiques
- Possibilité de suppression sur demande (droit à l’effacement)
- Absence de données personnelles inutiles dans la couche **Gold**

📄 Un document dédié est fourni :  
**`RGPD_CONFORMITE.md`**

---

## 📊 Analyses & exploitation

Les données finales sont exploitées via **PostgreSQL** à l’aide de requêtes analytiques démontrant :

- Des requêtes d’agrégation
- Des jointures multi-sources
- Des fonctions de fenêtrage (window functions)
- Des classements de type **Top-N**

📄 Les requêtes sont disponibles dans :  
**`sql/analyses.sql`**

# ▶️ Lancer le projet

## Prérequis

- Docker  
- Docker Compose  

## Lancement

```bash
docker compose up -d
docker compose run --rm pipeline
```

## Accès aux services

- **PostgreSQL** : `localhost:5432`
- **pgAdmin** : http://localhost:8080
- **MinIO** : http://localhost:9000 
