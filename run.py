import streamlit as st
import sys
import time
import pandas as pd
from io import StringIO
from db_operations.dbop_data import DatabaseOperationsData 
from table_executor.table_executor_utils import TableExecutorUtil
from data_writer.write_data_from_csv_to_db import WriteDataToDbFromCSV
from data_writer.main_category_writer import MainCategoryWriter
from data_writer.product_features_writer import ProductFeatureWriter

st.set_page_config(page_title="Hediyele - Product Management", page_icon="🎁", layout="centered")

st.sidebar.title("Hediyele - Product Management")
options = st.sidebar.radio(
    "Select an action:",
    [
        "Add Product",
        "Delete Product",
        "View Products",
        "Edit Main Categories",
        "Run Database Setup"
    ]
)

if options == "Run Database Setup":
    st.title("Run Database Setup")

    if st.button("Run Setup"):
        st.write("Database setup is starting...")

        output_capture = StringIO()
        sys.stdout = output_capture

        try:
            with st.spinner("Please Wait..."):
                #table_util = TableExecutorUtil()
                #st.write("[1/4] Creating tables...")
                #table_util.create_tables("table_executor/all_tables")
                #st.success("Tables created successfully!")
                #time.sleep(1)

                #st.write("[2/4] Writing data from CSV to database...")
                #data_writer = WriteDataToDbFromCSV()
                #data_writer.write_data("data")
                #st.success("Data written successfully!")
                #time.sleep(1)

                st.write("[3/4] Writing main categories...")
                main_category_writer = MainCategoryWriter()
                main_category_writer.write_main_categories()
                st.success("Main categories written successfully!")

                #st.write("[4/4] Calculating the Product Features...")
                #product_features_writer = ProductFeatureWriter()
                #product_features_writer.update_product_features()
                #st.success("Product Features written successfully!")

            st.success("Database setup completed successfully!")

        except Exception as e:
            st.error(f"An error occurred: {e}")
        finally:
            sys.stdout = sys.__stdout__

        output_log = output_capture.getvalue()
        st.text_area("Database Setup Logs", value=output_log, height=300)

elif options == "Add Product":
    st.title("Add Product")

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
            else:
                st.error("An error occurred while adding the product.")
        else:
            st.error("Please fill in all the fields.")

elif options == "Delete Product":
    st.title("Delete Product")

    db_operations = DatabaseOperationsData()

    total_products = db_operations.get_total_product_count()
    products_per_page = st.number_input("Products per page", min_value=5, max_value=500, value=10, step=5)
    page = st.number_input("Page", min_value=1, max_value=(total_products // products_per_page) + 1, value=1)

    offset = (page - 1) * products_per_page
    products = db_operations.fetch_products(limit=products_per_page, offset=offset)

    if products:
        st.write("### Product List - Click Delete to Remove")
        for product in products:
            product_id = product[0]
            product_name = product[4]
            category_name = product[1]

            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.write(f"**{product_name}** - Category: {category_name}")
            with col2:
                st.write(f"Price: {product[5]} | Rating: {product[6]}")
            with col3:
                if st.button("Delete", key=f"delete_{product_id}"):
                    success = db_operations.delete_product_from_database(product_id)
                    if success:
                        st.success(f"Product '{product_name}' successfully deleted!")
                    else:
                        st.error(f"Failed to delete product '{product_name}'")
    else:
        st.write("No products available to delete.")


elif options == "View Products":
    st.title("View Products")

    db_operations = DatabaseOperationsData()

    total_products = db_operations.get_total_product_count()
    products_per_page = st.number_input("Products per page", min_value=5, max_value=500, value=10, step=5)
    page = st.number_input("Page", min_value=1, max_value=(total_products // products_per_page) + 1, value=1)

    offset = (page - 1) * products_per_page
    products = db_operations.fetch_products(limit=products_per_page, offset=offset)

    if products:
        st.write("### Product List")
        df = pd.DataFrame(products, columns=["ID", "Category Name", "Main Category Name", "Link", "Name", "Price", "Rating"])
        st.dataframe(df)
    else:
        st.write("No products available.")
elif options == "Edit Main Categories":
    st.title("Edit Main Categories")

    file_path = "main_categories.txt"

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            file_content = file.read()
    except FileNotFoundError:
        file_content = ""
        st.warning("The file does not exist. A new file will be created upon saving.")

    edited_content = st.text_area("Edit Main Categories", value=file_content, height=400)

    if st.button("Save Changes"):
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(edited_content)
            main_category_writer = MainCategoryWriter()
            main_category_writer.clear_all_categories()
            main_category_writer.write_main_categories()

            st.success("Changes saved and categories updated successfully!")
        except Exception as e:
            st.error(f"An error occurred while saving: {e}")


