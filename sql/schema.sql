CREATE SCHEMA IF NOT EXISTS gold;

-- Books (Books to Scrape)
CREATE TABLE IF NOT EXISTS gold.books (
  book_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  category VARCHAR(255) NOT NULL,
  price NUMERIC(10,2) NOT NULL CHECK (price > 0),
  rating SMALLINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
  book_availability BOOLEAN NOT NULL, 
  img_url TEXT, 
  img_path TEXT
);

-- -- Quotes (Quotes to Scrape)
CREATE TABLE IF NOT EXISTS gold.authors (
  author_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS gold.quotes (
  quote_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  quote_text TEXT NOT NULL,
  author_id INT NOT NULL REFERENCES gold.authors(author_id)
);

CREATE TABLE gold.quote_tags (
  quote_id INT NOT NULL REFERENCES gold.quotes(quote_id) ON DELETE CASCADE,
  tag TEXT NOT NULL,
  PRIMARY KEY (quote_id, tag)
);


-- Products (Ecommerce)

-- CREATE TABLE IF NOT EXISTS gold.products (
--   product_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
--   product_name TEXT NOT NULL UNIQUE,
--   product_description TEXT NOT NULL,
--   category VARCHAR(255) NOT NULL,
--   price NUMERIC(10,2) NOT NULL CHECK (price > 0)
-- );

-- Partenaires (Excel) - RGPD: pas de PII en clair en Gold
CREATE TABLE IF NOT EXISTS gold.partners (
  partner_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  nom_librairie TEXT NOT NULL,
  adresse TEXT NOT NULL,
  code_postal TEXT,
  ville TEXT,
  specialite TEXT,
  ca_annuel NUMERIC(12,2),
  date_partenariat DATE,
  contact_hash TEXT,
  UNIQUE (nom_librairie, adresse, code_postal, ville)
);

-- Géocodage (API Adresse)
CREATE TABLE IF NOT EXISTS gold.partner_geocoding (
  partner_id BIGINT PRIMARY KEY REFERENCES gold.partners(partner_id) ON DELETE CASCADE,
  label TEXT,
  score NUMERIC(5,4),
  longitude NUMERIC(10,6),
  latitude NUMERIC(10,6)
);

-- -- Index utiles
-- CREATE INDEX IF NOT EXISTS idx_books_category ON gold.books(category);
-- CREATE INDEX IF NOT EXISTS idx_quotes_author ON gold.quotes(author_id);
-- CREATE INDEX IF NOT EXISTS idx_tags_tag ON gold.quote_tags(tag);
-- CREATE INDEX IF NOT EXISTS idx_partners_ville ON gold.partners(ville);
