DROP TABLE IF EXISTS book CASCADE;
CREATE TABLE book (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    author VARCHAR(255),
    publisher VARCHAR(255),
    price NUMERIC,
    currency VARCHAR(10),
    description TEXT,
    url VARCHAR(255)
);
