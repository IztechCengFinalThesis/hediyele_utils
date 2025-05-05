CREATE TABLE IF NOT EXISTS product_images (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES product(id) ON DELETE CASCADE,
    image_data BYTEA NOT NULL,
    image_order INTEGER DEFAULT 0
); 