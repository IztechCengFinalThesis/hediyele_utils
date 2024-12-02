CREATE TABLE IF NOT EXISTS categories_vectorized (
    id SERIAL PRIMARY KEY,
    category_id INTEGER UNIQUE NOT NULL REFERENCES categories(id),
    vector VECTOR(1536)
);