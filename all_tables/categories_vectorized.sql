CREATE TABLE IF NOT EXISTS categories_vectorized (
    id SERIAL PRIMARY KEY,
    category_id INT,
    vector FLOAT8[]
);