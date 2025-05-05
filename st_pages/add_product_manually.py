import streamlit as st
from db_operations.dbop_data import DatabaseOperationsData
from data_writer.main_category_writer import MainCategoryWriter
from data_writer.product_features_writer import ProductFeatureWriter
from utils.image_utils import ImageProcessor
import io

def app():
    st.title("Add Product Manually")

    product_name = st.text_input("Product Name", placeholder="Enter the product name you want to add")
    category_name = st.text_input("Category Name", placeholder="Enter the category name of the product")
    link = st.text_input("Product Link", placeholder="Enter the product link")
    price = st.number_input("Price", min_value=0.0, format="%.2f")
    description = st.text_area("Description", placeholder="Enter the product description")
    rating = st.slider("Rating", min_value=0.0, max_value=5.0, step=0.1)
    
    uploaded_file = st.file_uploader("Upload Product Image", type=["png", "jpg", "jpeg", "webp"])
    processed_image_bytes = None

    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        img_buffer = io.BytesIO(bytes_data)
        processed_image_bytes = ImageProcessor.prepare_image_for_db(img_buffer)
        if processed_image_bytes:
            st.image(processed_image_bytes, caption="Uploaded Image (Resized)", width=150)
        else:
            st.error("Could not process the uploaded image.")

    if st.button("Add Product"):
        if all([product_name, link, description, category_name, rating, price]):
            db_operations = DatabaseOperationsData()
            category_id = db_operations.add_category_if_not_exists(category_name)

            if category_id:
                new_product_id = db_operations.add_product_to_database(
                    product_name, category_id, link, price, description, rating
                )

                if new_product_id:
                    if processed_image_bytes:
                        img_success = db_operations.add_product_image(new_product_id, processed_image_bytes)
                        if not img_success:
                            st.warning("Product added, but failed to save the image.")
                    else:
                         st.warning("No image was uploaded or processed.")

                    main_category_writer = MainCategoryWriter()
                    main_category_writer.write_main_categories()
                    product_feature_writer = ProductFeatureWriter()
                    product_feature_writer.update_product_features()

                    st.success(f"Product '{product_name}' has been successfully added!")
                    st.rerun() 
                else:
                    st.error("An error occurred while adding the product (Product might already exist or DB error).")
            else:
                st.error("Could not find or create category.")

        else:
            st.error("Please fill in all the required fields (excluding image, which is optional).")
