CREATE TABLE IF NOT EXISTS product_features (
    id SERIAL PRIMARY KEY,
    
    -- age
    age_0_2 FLOAT DEFAULT 0.0, 
    age_3_5 FLOAT DEFAULT 0.0, 
    age_6_12 FLOAT DEFAULT 0.0, 
    age_13_18 FLOAT DEFAULT 0.0, 
    age_19_29 FLOAT DEFAULT 0.0, 
    age_30_45 FLOAT DEFAULT 0.0, 
    age_45_65 FLOAT DEFAULT 0.0, 
    age_65_plus FLOAT DEFAULT 0.0, 
    
    -- gender
    gender_male FLOAT DEFAULT 0.0, 
    gender_female FLOAT DEFAULT 0.0, 
    
    -- special
    special_birthday FLOAT DEFAULT 0.0, 
    special_anniversary FLOAT DEFAULT 0.0, 
    special_valentines FLOAT DEFAULT 0.0,
    special_new_year FLOAT DEFAULT 0.0,
    special_house_warming FLOAT DEFAULT 0.0,
    special_mothers_day FLOAT DEFAULT 0.0,
    special_fathers_day FLOAT DEFAULT 0.0,
    special_other FLOAT DEFAULT 0.0,

    -- interest
    interest_sports FLOAT DEFAULT 0.0, 
    interest_music FLOAT DEFAULT 0.0, 
    interest_books FLOAT DEFAULT 0.0, 
    interest_technology FLOAT DEFAULT 0.0, 
    interest_travel FLOAT DEFAULT 0.0, 
    interest_art FLOAT DEFAULT 0.0, 
    interest_food FLOAT DEFAULT 0.0, 
    interest_fitness FLOAT DEFAULT 0.0, 
    interest_health FLOAT DEFAULT 0.0, 
    interest_photography FLOAT DEFAULT 0.0, 
    interest_fashion FLOAT DEFAULT 0.0, 
    interest_pets FLOAT DEFAULT 0.0, 
    interest_home_decor FLOAT DEFAULT 0.0, 
    interest_movies_tv FLOAT DEFAULT 0.0
);
