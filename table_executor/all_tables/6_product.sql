CREATE TABLE IF NOT EXISTS product (
    id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES categories(id) ON DELETE CASCADE,
    product_features_id INTEGER REFERENCES product_features(id) ON DELETE CASCADE,
    link TEXT,
    product_name TEXT,
    price NUMERIC,
    description TEXT,
    rating TEXT
);
