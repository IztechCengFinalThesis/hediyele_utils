CREATE TABLE blind_test_recommendations (
	id serial4 NOT NULL,
	blind_test_session_id int4 NOT NULL,
	algorithm_name text NOT NULL,
	recommended_product_id int4 NOT NULL,
	is_selected bool DEFAULT false NOT NULL,
	recommended_order int4 NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP NULL,
	bad_recommendation bool DEFAULT false NULL,
	CONSTRAINT blind_test_recommendations_pkey PRIMARY KEY (id),
	CONSTRAINT blind_test_recommendations_blind_test_session_id_fkey FOREIGN KEY (blind_test_session_id) REFERENCES public.blind_test_session(id) ON DELETE CASCADE
);
CREATE TABLE blind_test_session (
	id serial4 NOT NULL,
	parameters jsonb NOT NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP NULL,
	mail text NULL,
	CONSTRAINT blind_test_session_pkey PRIMARY KEY (id)
);