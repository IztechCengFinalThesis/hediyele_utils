import streamlit as st
import sys
import time
from io import StringIO
from table_executor.table_executor_utils import TableExecutorUtil
from data_writer.write_data_from_csv_to_db import WriteDataToDbFromCSV
from data_writer.main_category_writer import MainCategoryWriter
from data_writer.product_features_writer import ProductFeatureWriter

def app():
    st.title("Run Database Setup")

    if st.button("Run Setup"):
        st.write("Database setup is starting...")

        output_capture = StringIO()
        sys.stdout = output_capture

        try:
            with st.spinner("Please Wait..."):
                table_util = TableExecutorUtil()
                st.write("[1/4] Creating tables...")
                table_util.create_tables("table_executor/all_tables")
                st.success("Tables created successfully!")
                time.sleep(1)

                st.write("[2/4] Writing data from CSV to database...")
                data_writer = WriteDataToDbFromCSV()
                data_writer.write_data("data")
                st.success("Data written successfully!")
                time.sleep(1)

                st.write("[3/4] Writing main categories...")
                main_category_writer = MainCategoryWriter()
                main_category_writer.write_main_categories()
                st.success("Main categories written successfully!")

                st.write("[4/4] Calculating the Product Features...")
                product_features_writer = ProductFeatureWriter()
                product_features_writer.update_product_features()
                st.success("Product Features written successfully!")

                st.success("Database setup completed successfully!")
        except Exception as e:
            st.error(f"An error occurred: {e}")
        finally:
            sys.stdout = sys.__stdout__

        output_log = output_capture.getvalue()
        st.text_area("Database Setup Logs", value=output_log, height=300)
