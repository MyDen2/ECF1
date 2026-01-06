# 📘 Dossier d’Architecture Technique (DAT)

## 1. Choix d’architecture globale

### Architecture proposée

L’architecture retenue est une **architecture de type Lakehouse**, combinant :
- un **Data Lake logique** pour les données brutes et intermédiaires (Bronze + Silver)
- un **Data Warehouse relationnel** pour les données analytiques finales

Elle est structurée en **trois couches** :
- **Bronze** : données brutes (JSON, Excel)
- **Silver** : données nettoyées et conformes (CSV)
- **Gold** : données finales relationnelles dans PostgreSQL (SQL analytique)

---

### Justification du choix

Cette architecture permet :
- de conserver l’historique des données sources (traçabilité)
- de séparer clairement extraction, transformation et chargement
- de faciliter le **debug** (on peut rejouer à partir du Bronze ou Silver)
- d’offrir des performances SQL élevées pour l’analyse
- de rester simple à déployer via Docker

---

### Comparaison avec une alternative

| Alternative | Pourquoi non retenue |
|------------|---------------------|
| Data Warehouse seul | Pas de conservation des données brutes |
| Data Lake pur | Faibles performances SQL |
| NoSQL (MongoDB) | Peu adapté aux requêtes analytiques complexes |
| Architecture micro-services | Surdimensionnée pour le besoin |

---

### Avantages / Inconvénients

**Avantages**
- Modularité et évolutivité
- Traçabilité complète des données
- Forte compatibilité analytique SQL
- Séparation claire des responsabilités

**Inconvénients**
- Multiplication des fichiers intermédiaires
- Gestion plus complexe qu’un simple ETL direct
- Gestion du stockage si les volumes augmentent fortement

---

## 2. Choix des technologies

### 2.1 Stockage des données brutes (Bronze)

**Choix :** système de fichiers local monté dans Docker (`/app/data/bronze/...`)  
**Formats :** `JSON` (scraping Books/Quotes) + `XLSX` (partners)

**Justification :**
- Conservation fidèle des sources (snapshot)
- Compatibilité immédiate avec Python
- Simple à déployer

**Alternative comparée :**
- Amazon S3 / HDFS → excellent pour la scalabilité mais non retenu en raison de sa complexité excessive pour le contexte

---

### 2.2 Données transformées (Silver)

**Choix :** fichiers `CSV` versionnés par `run_id`  
**Exemples :**
- `data/silver/run_id=.../books_clean.csv`
- `data/silver/run_id=.../quotes_clean.csv`
- `data/silver/run_id=.../partners_clean.csv`

**Justification :**
- Lisibilité humaine (utile pour les audits)
- Compatibilité avec PostgreSQL
- Débogage facilité

**Alternative comparée :**
- Parquet → plus performant mais inutile ici vu les volumes

---

### 2.3 Stockage final & interrogation SQL (Gold)

**Choix :** PostgreSQL 16

**Justification :**
- SQL analytique complet (CTE, window functions, agrégations, jointures)
- Fonctions de fenêtrage et agrégations
- Robute, open-source, standard

**Alternative comparée :**
- SQLite → non adapté au multi-processus
- MySQL → moins riche analytiquement
- BigQuery → hors périmètre local (cloud)

---

### 2.4 Stockage des images

**Choix :** MinIO (stockage objet compatible S3), la base de données ne stocke que l’URL

**Justification :**
- Évite la surcharge du disque locale
- Scalabilité native
- La base ne stocke que les URL des images

---

## 3. Organisation des données

### 3.1 Structure logique

data/
│   ├── bronze/
│   │   └── run_id=YYYY-MM-DDTHH-MM-SS/
│   │       ├── partners_source.xlsx
│   │       ├── books_raw.json
│   │       └── quotes_raw.json
│   │
│   └── silver/
│   |    └── run_id=YYYY-MM-DDTHH-MM-SS/
│   |        ├── partners_clean.csv
│   |        ├── books_clean.csv
│   |        └── quotes_clean.csv
|   |___partenaire_librairies.xlsx

Le fichier partenaire_librairies.xlsx correspond au fichier excel initial, à partir duquel on extrait les données. 

### 3.2 Pourquoi des couches (Bronze/Silver/Gold)

- **Bronze** : snapshot des sources (audit, reproductibilité)
- **Silver** : transformations contrôlées et conformes (qualité, RGPD)
- **Gold** : modèle final analysable et requêtable (SQL)

### 3.3 Convention de nommage

- `run_id` au format ISO (`YYYY-MM-DDTHH-MM-SS`)
- colonnes en `snake_case`
- tables finales préfixées par le schéma `gold.`
- fichiers : `<dataset>_<stage>.{json|csv|xlsx}`

---

## 4. Modélisation des données

### 4.1 Modèle de données proposé

Nous utilisons un **modèle relationnel analytique** en couche Gold (PostgreSQL),
avec :
- tables de faits principales (books, quotes, partners)
- tables de dimensions / références (authors, tags)
- tables techniques (partner_geocoding)

### 4.2 Schéma

- `gold.books`
  - informations sur les livres : titre, catégorie, prix, note, disponibilité, image
- `gold.authors`
  - référentiel auteurs (unique)
- `gold.quotes`
  - citations liées à un auteur (`author_id`)
- `gold.quote_tags`
  - tags par citation (relation n-n)
- `gold.partners`
  - librairies partenaires (données nettoyées RGPD + hash contact)
- `gold.partner_geocoding`
  - coordonnées GPS liées à `partners` (1-1)

### 4.3 Justification du modèle

- assure la cohérence via contraintes et clés étrangères
- facilite les jointures analytiques (ex : quotes ↔ authors)
- séparation des données partenaires (métier) et du géocodage (technique)
- respecte le RGPD en évitant toute donnée contact en clair

---

## 5. Conformité RGPD

### 5.1 Données personnelles identifiées

**Source Excel Partners**
- adresse (professionnelle) : `adresse`, `code_postal`, `ville`
- potentielle donnée sensible : contact (mail/téléphone) **non stocké en clair**

**Source API Adresse**
- coordonnées géographiques : `latitude`, `longitude`

**Sources Web scraping**
- Books/Quotes : pas de données personnelles

### 5.2 Mesures de protection mises en œuvre

- suppression des contacts en clair : seul `contact_hash` est conservé
- hashing (ex : SHA-256) irréversible du contact
- stockage par couches (brut vs clean) avec séparation claire
- accès à la base via container Docker uniquement (réseau isolé)

### 5.3 Droit à l’effacement (suppression sur demande)

- suppression d’un partenaire possible via `partner_id`
- suppression en cascade des données associées grâce à :
  - `gold.partner_geocoding.partner_id REFERENCES gold.partners(partner_id) ON DELETE CASCADE`
- le `contact_hash` ne permet pas de ré-identifier une personne sans la donnée originale

---

## Conclusion

L’architecture Lakehouse (Bronze/Silver/Gold) + PostgreSQL 16 + MinIO :
- répond aux besoins d’extraction multi-sources
- garantit traçabilité et reproductibilité via `run_id`
- permet un SQL analytique robuste en couche Gold
- reste cohérente avec le RGPD grâce au hashing et à la minimisation des données
