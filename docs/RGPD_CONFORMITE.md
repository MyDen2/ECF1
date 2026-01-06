# RGPD – Documentation de conformité

## 1. Présentation générale

Ce document décrit les mesures mises en œuvre afin d’assurer la conformité du projet **ECF1 – Plateforme Data** au Règlement Général sur la Protection des Données (RGPD).

La plateforme collecte, transforme et stocke des données issues de sources publiques (scraping web), de fichiers fournis par des partenaires (Excel) et d’API publiques.  
Aucune donnée personnelle sensible ou relevant de la vie privée n’est exploitée à des fins commerciales ou de profilage individuel.

---

## 2. Inventaire des données personnelles collectées

### 2.1 Données issues du fichier partenaires (Excel)

| Donnée | Description | Caractère personnel |
|------|------------|---------------------|
| nom_librairie | Nom commercial de la librairie | Non |
| adresse | Adresse postale | Indirectement |
| code_postal | Code postal | Indirectement |
| ville | Ville | Indirectement |
| specialite | Spécialité commerciale | Non |
| ca_annuel | Chiffre d’affaires annuel | Donnée sensible entreprise |
| date_partenariat | Date de partenariat | Non |
| contact (email / nom) | Contact partenaire (source initiale) | **Oui (avant anonymisation)** |

Les données de contact sont **hachées** et **ne sont jamais stockées en clair** dans la base finale.

---

### 2.2 Données issues du scraping web

| Source | Données collectées | Caractère personnel |
|------|------------------|---------------------|
| Books to Scrape | Titre, catégorie, prix, note, image | Non |
| Quotes to Scrape | Citation, auteur | Donnée publique |

Les données collectées proviennent exclusivement de **sites publics à vocation pédagogique**, sans restriction d’accès.

---

### 2.3 Données issues d’API publiques

| API | Données | Caractère personnel |
|----|--------|---------------------|
| API Adresse (gouv.fr) | Coordonnées géographiques d’une adresse | Indirectement |

Les données sont liées à des **personnes morales (librairies)** et non à des personnes physiques.

---

## 3. Base légale du traitement

| Donnée | Base légale |
|------|------------|
| Données partenaires | Intérêt légitime (analyse commerciale, cartographie) |
| Données de contact | Consentement implicite du partenaire + anonymisation |
| Données de géolocalisation | Intérêt légitime |
| Données issues du scraping | Données publiques |

Aucune donnée n’est utilisée à des fins de prospection commerciale ou de prise de décision automatisée concernant des personnes physiques.

---

## 4. Mesures de protection mises en œuvre

### 4.1 Anonymisation / pseudonymisation

- Les données de contact partenaires sont **hachées (SHA-256)** dès la phase de transformation (Silver)
- Aucune donnée personnelle n’est stockée en clair dans la couche Gold

### 4.2 Séparation des couches de données

- **Bronze** : données sources brutes (accès restreint)
- **Silver** : données nettoyées et anonymisées
- **Gold** : données exploitables, sans information personnelle directe

---

### 4.3 Sécurité technique

- Accès base de données restreint par authentification
- Conteneurisation Docker
- Données stockées localement, non exposées publiquement
- Images stockées dans un stockage objet (MinIO), référencées uniquement par URL

---

### 4.4 Minimisation des données

- Seules les données strictement nécessaires aux objectifs analytiques sont conservées
- Aucune conservation de données inutiles (logs nettoyés, snapshots horodatés)

---

## 5. Durée de conservation

| Type de données | Durée |
|---------------|-------|
| Données partenaires | Tant que le partenariat est actif |
| Données de géocodage | Réactualisables à la demande |
| Données de scraping | Illimitée (données publiques) |

---

## 6. Procédure de suppression sur demande (Droit à l’effacement)

En cas de demande de suppression par un partenaire :

1. Identification du partenaire via ses attributs commerciaux (nom, adresse)
2. Suppression des enregistrements dans :
   - `gold.partners`
   - `gold.partner_geocoding`
3. Regénération éventuelle des agrégats analytiques
4. Vérification qu’aucune donnée personnelle n’est conservée dans les logs ou snapshots

La suppression est définitive et irréversible.

---

## 7. Conclusion

La plateforme met en œuvre :
- une **collecte responsable**
- une **anonymisation systématique**
- une **architecture conforme au principe de privacy by design**

Le projet est conforme aux exigences du RGPD dans le cadre d’un traitement analytique et pédagogique.
