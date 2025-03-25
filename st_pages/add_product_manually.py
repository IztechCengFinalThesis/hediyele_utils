import streamlit as st
from db_operations.dbop_data import DatabaseOperationsData
from data_writer.main_category_writer import MainCategoryWriter
from data_writer.product_features_writer import ProductFeatureWriter

def app():
    st.title("Add Product Manually")

    product_name = st.text_input("Product Name", placeholder="Enter the product name you want to add")
    category_name = st.text_input("Category Name", placeholder="Enter the category name of the product")
    link = st.text_input("Product Link", placeholder="Enter the product link")
    price = st.number_input("Price", min_value=0.0, format="%.2f")
    description = st.text_area("Description", placeholder="Enter the product description")
    rating = st.slider("Rating", min_value=0.0, max_value=5.0, step=0.1)

    if st.button("Add Product"):
        if all([product_name, link, description, category_name, rating, price]):
            db_operations = DatabaseOperationsData()
            category_id = db_operations.add_category_if_not_exists(category_name)
            success = db_operations.add_product_to_database(product_name, category_id, link, price, description, rating)

            main_category_writer = MainCategoryWriter()
            main_category_writer.write_main_categories()

            product_feature_writer = ProductFeatureWriter()
            product_feature_writer.update_product_features()

            if success:
                st.success(f"Product '{product_name}' has been successfully added!")
                st.rerun() 
            else:
                st.error("An error occurred while adding the product.")
        else:
            st.error("Please fill in all the fields.")
