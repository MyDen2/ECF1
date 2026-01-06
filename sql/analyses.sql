-- =========================================================
-- Livrable 3.4 : Requêtes analytiques
-- =========================================================

------------------------------------------------------------
-- 1) Requête d’agrégation simple
-- Nombre de livres, prix moyen et note moyenne par catégorie
------------------------------------------------------------
SELECT
  category,
  COUNT(*)                       AS nb_books,
  ROUND(AVG(price), 2)           AS avg_price,
  ROUND(AVG(rating)::numeric, 2) AS avg_rating
FROM gold.books
GROUP BY category
ORDER BY nb_books DESC;


------------------------------------------------------------
-- 2) Requête avec jointure
-- Nombre de citations par auteur
------------------------------------------------------------
SELECT
  a.name,
  COUNT(q.quote_id) AS nb_quotes
FROM gold.authors a
JOIN gold.quotes q
  ON q.author_id = a.author_id
GROUP BY a.name
ORDER BY nb_quotes DESC;


------------------------------------------------------------
-- 3) Requête avec fonction de fenêtrage (window function)
-- Classement des livres par prix à l’intérieur de chaque catégorie
------------------------------------------------------------
SELECT
  category,
  title,
  price,
  ROUND(AVG(price) OVER (PARTITION BY category), 2) AS avg_price_category,
  DENSE_RANK() OVER (PARTITION BY category ORDER BY price DESC) AS rank_in_category
FROM gold.books
ORDER BY category, rank_in_category;


------------------------------------------------------------
-- 4) Requête de classement (Top N)
-- Top 10 des partenaires par chiffre d’affaires
------------------------------------------------------------
SELECT
  nom_librairie,
  ville,
  ca_annuel
FROM gold.partners
ORDER BY ca_annuel DESC
LIMIT 10;


------------------------------------------------------------
-- 5) Requête croisant au moins 2 sources de données
-- Croisement Partners + Géocodage :
-- CA total et qualité moyenne du géocodage par ville
------------------------------------------------------------
SELECT
  p.ville,
  COUNT(*)                     AS nb_partners,
  ROUND(SUM(p.ca_annuel), 2)   AS ca_total,
  ROUND(AVG(g.score)::numeric, 4) AS avg_geocode_score
FROM gold.partners p
JOIN gold.partner_geocoding g
  ON g.partner_id = p.partner_id
GROUP BY p.ville
ORDER BY ca_total DESC;
