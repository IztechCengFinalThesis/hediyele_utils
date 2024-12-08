CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    category_name TEXT UNIQUE NOT NULL,
    main_category_id INTEGER REFERENCES main_categories(id) ON DELETE CASCADE  
);
