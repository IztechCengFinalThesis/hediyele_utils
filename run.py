import streamlit as st
import sys
import time
from io import StringIO
from table_executor.table_executor_utils import TableExecutorUtil
from data_writer.write_data_from_csv_to_db import WriteDataToDbFromCSV
from vectorizer_utils.vectorizer_utils import CategoryVectorizer
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
            with st.spinner("Lütfen bekleyiniz..."):
                table_util = TableExecutorUtil()
                st.write("[1/5] Creating tables...")
                table_util.create_tables("table_executor/all_tables")
                st.success("Tables created successfully!")
                time.sleep(1)

                st.write("[2/5] Writing data from CSV to database...")
                data_writer = WriteDataToDbFromCSV()
                data_writer.write_data("data")
                st.success("Data written successfully!")
                time.sleep(1)

                st.write("[3/5] Vectorizing categories...")
                category_vectorizer = CategoryVectorizer()
                category_vectorizer.vectorize_categories()
                st.success("Categories vectorized successfully!")
                time.sleep(1)

                st.write("[4/5] Writing main categories...")
                main_category_writer = MainCategoryWriter()
                main_category_writer.write_main_categories()
                st.success("Main categories written successfully!")

                #st.write("[5/5] Calculating the Product Features...")
                #product_features_writer = ProductFeatureWriter()
                #update_product_features()
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
    if st.button("Add"):
        if product_name:
            st.success(f"'{product_name}' has been successfully added!")
        else:
            st.error("Please enter a product name!")

elif options == "Delete Product":
    st.title("Delete Product")
    product_id = st.text_input("Product ID", placeholder="Enter the product ID you want to delete")
    if st.button("Delete"):
        if product_id:
            st.success(f"Product with ID '{product_id}' has been successfully deleted!")
        else:
            st.error("Please enter a product ID!")

elif options == "View Products":
    st.title("View Products")
    st.write("Here you will see the list of all added products.")

elif options == "Edit Main Categories":
    st.title("Edit Main Categories")
    st.write("Here you can edit main categories.")

