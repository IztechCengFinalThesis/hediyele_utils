DROP TABLE IF EXISTS categories_vectorized;
CREATE TABLE categories_vectorized (
    id SERIAL PRIMARY KEY,
    category_id INT,
    vector FLOAT8[]
);