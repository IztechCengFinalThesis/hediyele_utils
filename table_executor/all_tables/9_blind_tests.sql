CREATE TABLE IF NOT EXISTS blind_test_requests (
    id SERIAL PRIMARY KEY,
    parameters JSONB NOT NULL,
    user_chosen_product_id INTEGER REFERENCES product(id),
    user_chosen_algorithm_name TEXT,  
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS blind_test_recommendations (
    id SERIAL PRIMARY KEY,
    blind_test_request_id INTEGER NOT NULL REFERENCES blind_test_requests(id) ON DELETE CASCADE,
    algorithm_name TEXT NOT NULL, 
    recommended_product_id INTEGER NOT NULL REFERENCES product(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
