DROP TABLE IF EXISTS product CASCADE;
CREATE TABLE product (
    id SERIAL PRIMARY KEY,
    category TEXT,
    link TEXT,
    product_name TEXT,
    price NUMERIC,
    description TEXT,
    rating TEXT
);
