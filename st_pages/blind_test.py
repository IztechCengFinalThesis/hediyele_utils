import random
import streamlit as st
from db_operations.dbop_blind_test import DatabaseOperationsBlindTest
from constants import GENDERS, AGE_GROUPS, SPECIAL_OCCASIONS, INTERESTS
from blind_tests.blind_test_algorithms import RecommendationService

def select_random_features() -> dict:
    features = {}
    age_key = random.choice(list(AGE_GROUPS.keys()))
    features[age_key] = 1.0
    gender_key = random.choice(list(GENDERS.keys()))
    features[gender_key] = 1.0
    if random.random() < 0.5:
        special_key = random.choice(list(SPECIAL_OCCASIONS.keys()))
        features[special_key] = 1.0
    all_interest_keys = list(INTERESTS.keys())
    num_interests = random.randint(1, min(3, len(all_interest_keys)))
    selected_interests = random.sample(all_interest_keys, num_interests)
    for key in selected_interests:
        features[key] = 1.0
    return features

def initialize_blind_test():
    features = select_random_features()
    rec_service = RecommendationService()
    recommendations = rec_service.get_blind_recommendations(features)
    st.session_state["blind_test_features"] = features
    st.session_state["blind_test_recommendations"] = recommendations

def app():
    st.title("Blind Test - Automatic Product Recommendation")
    
    if st.button("Refresh Random Features"):
        initialize_blind_test()
        st.rerun()
    
    if "blind_test_features" not in st.session_state or "blind_test_recommendations" not in st.session_state:
        initialize_blind_test()

    st.subheader("Randomly Selected Features")
    features = st.session_state["blind_test_features"]
    display_features = []
    for key, label in AGE_GROUPS.items():
        if features.get(key) == 1.0:
            display_features.append(label)
    for key, label in GENDERS.items():
        if features.get(key) == 1.0:
            display_features.append(label)
    for key, label in SPECIAL_OCCASIONS.items():
        if features.get(key) == 1.0:
            display_features.append(label)
    selected_interests = [label for key, label in INTERESTS.items() if features.get(key) == 1.0]
    if selected_interests:
        display_features.append("Interests: " + ", ".join(selected_interests))
    st.markdown("\n".join(["- " + feature for feature in display_features]))

    st.subheader("Algorithm Recommendations")
    recommendations = st.session_state["blind_test_recommendations"]
    rec_options = []
    rec_mapping = {}
    for rec in recommendations:
        option_label = f"Algorithm: {rec['algorithm_name']} - Recommended Product Name: {rec['product_name']}"
        rec_options.append(option_label)
        rec_mapping[option_label] = rec
    selected_option = st.radio("Please select one of the recommendations:", options=rec_options)

    if st.button("Save Selection"):
        chosen_rec = rec_mapping[selected_option]
        chosen_alg_name = chosen_rec["algorithm_name"]
        chosen_product_id = chosen_rec["product_id"]
        db_ops = DatabaseOperationsBlindTest()
        request_id = db_ops.create_blind_test_request(st.session_state["blind_test_features"])
        for rec in recommendations:
            db_ops.record_recommendation(request_id, rec["algorithm_name"], rec["product_id"])
        if db_ops.record_user_selection(request_id, chosen_product_id, chosen_alg_name):
            st.success("Your selection has been saved successfully.")
            initialize_blind_test()
            st.rerun()
        else:
            st.error("Error saving the selection.")

if __name__ == "__main__":
    app()
