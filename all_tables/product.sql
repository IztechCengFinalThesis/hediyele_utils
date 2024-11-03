CREATE TABLE IF NOT EXISTS product (
    id SERIAL PRIMARY KEY,
    category TEXT,
    link TEXT,
    product_name TEXT,
    price NUMERIC,
    description TEXT,
    rating TEXT
);
