from selenium_utils.scrapper import HepsiBuradaScraper, AmazonScraper

# Product features and categorization prompts
FEATURE_PROMPT = "You are a product analyst that scores products based on their relevance to specific features."
CATEGORY_PROMPT = "You are a helpful assistant that categorizes products."

# Age group mappings
AGE_GROUPS = {
    "age_0_2": "Ages 0-2",
    "age_3_5": "Ages 3-5",
    "age_6_12": "Ages 6-12",
    "age_13_18": "Ages 13-18",
    "age_19_29": "Ages 19-29",
    "age_30_45": "Ages 30-45",
    "age_45_65": "Ages 45-65",
    "age_65_plus": "Ages 65+"
}

# Gender mappings
GENDERS = {
    "gender_male": "Male Users",
    "gender_female": "Female Users"
}

# Special occasion mappings
SPECIAL_OCCASIONS = {
    "special_birthday": "Birthday Gifts",
    "special_anniversary": "Anniversary Gifts",
    "special_valentines": "Valentine's Day",
    "special_new_year": "New Year",
    "special_house_warming": "House Warming",
    "special_mothers_day": "Mother's Day",
    "special_fathers_day": "Father's Day",
    "special_other": "Other"
}

# Interest category mappings
INTERESTS = {
    "interest_sports": "Sports",
    "interest_music": "Music",
    "interest_books": "Books",
    "interest_technology": "Technology",
    "interest_travel": "Travel",
    "interest_art": "Art",
    "interest_food": "Food",
    "interest_fitness": "Fitness",
    "interest_health": "Health",
    "interest_photography": "Photography",
    "interest_fashion": "Fashion",
    "interest_pets": "Pets",
    "interest_home_decor": "Home Decor",
    "interest_movies_tv": "Movies & TV"
}

# Combined dictionary of all feature mappings
ALL_FEATURES = {
    **AGE_GROUPS,
    **GENDERS,
    **SPECIAL_OCCASIONS,
    **INTERESTS
}

WEB_SITES = {
    "HepsiBurada": HepsiBuradaScraper,
    "Amazon": AmazonScraper
}