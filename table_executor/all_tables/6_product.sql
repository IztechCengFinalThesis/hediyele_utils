CREATE TABLE IF NOT EXISTS product (
    id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES categories(id) ON DELETE CASCADE,
    product_features_id INTEGER REFERENCES product_features(id) ON DELETE CASCADE,
    link TEXT UNIQUE NOT NULL,
    product_name TEXT,
    price NUMERIC,
    description TEXT,
    rating TEXT,
    site TEXT NOT NULL CHECK (site IN ('HepsiBurada', 'Amazon')),
    is_last_7_days_lower_price BOOLEAN DEFAULT FALSE,
    is_last_30_days_lower_price BOOLEAN DEFAULT FALSE
);
