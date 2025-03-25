CREATE TABLE IF NOT EXISTS price_changes (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES product(id) ON DELETE CASCADE,
    old_price NUMERIC NOT NULL,
    new_price NUMERIC NOT NULL,
    created_date DATE NOT NULL DEFAULT CURRENT_DATE
); 