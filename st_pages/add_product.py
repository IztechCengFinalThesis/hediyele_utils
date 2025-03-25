import streamlit as st
from constants import WEB_SITES
from db_operations.dbop_data import DatabaseOperationsData
from data_writer.main_category_writer import MainCategoryWriter
from data_writer.product_features_writer import ProductFeatureWriter
from constants import AGE_GROUPS, GENDERS, SPECIAL_OCCASIONS, INTERESTS 

def app():
    st.title("Add Product")

    if "product_data" not in st.session_state:
        st.session_state.product_data = {}
    if "product_features" not in st.session_state:
        st.session_state.product_features = None
    if "current_step" not in st.session_state:
        st.session_state.current_step = "input"  
    if "form_data" not in st.session_state:
        st.session_state.form_data = {}
    
    if st.session_state.current_step == "input":
        site_option = st.selectbox("Select Site", list(WEB_SITES.keys()))
        link_input = st.text_input("Enter Product Link", placeholder="Enter the product link", key="link_input")

        if st.button("Fetch Product Data"):
            if link_input:
                scraper_class = WEB_SITES.get(site_option)
                if scraper_class:
                    scraper = scraper_class()
                    st.session_state.product_data = scraper.get_product_details(link_input)
                    scraper.quit()
            else:
                st.error("Please enter a product link.")

        product_data = st.session_state.product_data

        product_name = st.text_input("Product Name", value=product_data.get("Product Name", ""), key="product_name")
        category_name = st.text_input("Category Name", value=product_data.get("Category", ""), key="category_name")
        link = st.text_input("Product Link", value=product_data.get("Link", link_input), key="product_link")
        price = st.text_input("Price", value=product_data.get("Price", ""), key="price")
        description = st.text_area("Description", value=product_data.get("Description", ""), key="description")
        rating = st.text_input("Rating", value=product_data.get("Rating", ""), key="rating")

        if st.button("Calculate Features"):
            if all([product_name, link, description, category_name, rating, price]):
                # Store form data in session state
                st.session_state.form_data = {
                    "product_name": product_name,
                    "category_name": category_name,
                    "link": link,
                    "price": price,
                    "description": description,
                    "rating": rating
                }
                
                product_info = {
                    "product_name": product_name,
                    "category_name": category_name,
                    "description": description
                }
                
                feature_writer = ProductFeatureWriter()
                st.session_state.product_features = feature_writer.calculate_product_features(product_info)
                st.session_state.current_step = "review"
                st.rerun()
            else:
                st.error("Please fill in all the fields.")

    elif st.session_state.current_step == "review":
        st.subheader("Review Product Features")
        
        features = st.session_state.product_features
        edited_features = {}
        
        # Age Groups Section
        st.write("### Age Groups")
        col1, col2 = st.columns(2)
        for i, feature in enumerate(AGE_GROUPS):
            col = col1 if i % 2 == 0 else col2
            edited_features[feature] = col.slider(
                AGE_GROUPS[feature], 
                min_value=0.0, 
                max_value=10.0, 
                value=float(features.get(feature, 0)),
                step=0.1
            )

        # Gender Section
        st.write("### Gender")
        col1, col2 = st.columns(2)
        for i, feature in enumerate(GENDERS):
            col = col1 if i % 2 == 0 else col2
            edited_features[feature] = col.slider(
                GENDERS[feature],
                min_value=0.0,
                max_value=10.0,
                value=float(features.get(feature, 0)),
                step=0.1
            )

        # Special Occasions Section
        st.write("### Special Occasions")
        col1, col2 = st.columns(2)
        for i, feature in enumerate(SPECIAL_OCCASIONS):
            col = col1 if i % 2 == 0 else col2
            edited_features[feature] = col.slider(
                SPECIAL_OCCASIONS[feature],
                min_value=0.0,
                max_value=10.0,
                value=float(features.get(feature, 0)),
                step=0.1
            )

        # Interests Section
        st.write("### Interests")
        col1, col2 = st.columns(2)
        for i, feature in enumerate(INTERESTS):
            col = col1 if i % 2 == 0 else col2
            edited_features[feature] = col.slider(
                INTERESTS[feature],
                min_value=0.0,
                max_value=10.0,
                value=float(features.get(feature, 0)),
                step=0.1
            )

        col1, col2 = st.columns(2)
        if col1.button("Back to Edit"):
            st.session_state.current_step = "input"
            st.rerun()

        if col2.button("Confirm and Save"):
            db_operations = DatabaseOperationsData()
            category_id = db_operations.add_category_if_not_exists(st.session_state.form_data["category_name"])
            
            success = db_operations.add_product_to_database(
                st.session_state.form_data["product_name"],
                category_id,
                st.session_state.form_data["link"],
                st.session_state.form_data["price"],
                st.session_state.form_data["description"],
                st.session_state.form_data["rating"]
            )

            if success:
                feature_writer = ProductFeatureWriter()
                feature_writer.save_product_features(db_operations.last_inserted_id(), edited_features)
                
                main_category_writer = MainCategoryWriter()
                main_category_writer.write_main_categories()

                st.success("Product and features have been successfully added!")
                st.session_state.current_step = "input"
                st.session_state.product_data = {}
                st.session_state.product_features = None
                st.session_state.form_data = {}
                st.rerun()
            else:
                st.error("An error occurred while adding the product.")
