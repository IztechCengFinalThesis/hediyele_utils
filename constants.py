# Product features and categorization prompts
FEATURE_PROMPT = "You are a product analyst that scores products based on their relevance to specific features."
CATEGORY_PROMPT = "You are a helpful assistant that categorizes products."

# Age group mappings
AGE_GROUPS = {
    "age_0_2": "ages 0-2",
    "age_3_5": "ages 3-5",
    "age_6_12": "ages 6-12",
    "age_13_18": "ages 13-18",
    "age_19_29": "ages 19-29",
    "age_30_45": "ages 30-45",
    "age_45_65": "ages 45-65",
    "age_65_plus": "ages 65 and above"
}

# Gender mappings
GENDERS = {
    "gender_male": "male users",
    "gender_female": "female users"
}

# Special occasion mappings
SPECIAL_OCCASIONS = {
    "special_birthday": "birthday gifts",
    "special_anniversary": "anniversary gifts",
    "special_valentines": "Valentine's Day gifts",
    "special_new_year": "New Year gifts",
    "special_house_warming": "house warming gifts",
    "special_mothers_day": "Mother's Day gifts",
    "special_fathers_day": "Father's Day gifts"
}

# Interest category mappings
INTERESTS = {
    "interest_sports": "sports enthusiasts",
    "interest_music": "music lovers",
    "interest_books": "book readers",
    "interest_technology": "tech enthusiasts",
    "interest_travel": "travelers",
    "interest_art": "art lovers",
    "interest_food": "food enthusiasts",
    "interest_fitness": "fitness enthusiasts",
    "interest_health": "health conscious people",
    "interest_photography": "photography enthusiasts",
    "interest_fashion": "fashion enthusiasts",
    "interest_pets": "pet owners",
    "interest_home_decor": "home decoration enthusiasts",
    "interest_movies_tv": "movie and TV show fans"
}

# Combined dictionary of all feature mappings
ALL_FEATURES = {
    **AGE_GROUPS,
    **GENDERS,
    **SPECIAL_OCCASIONS,
    **INTERESTS
}