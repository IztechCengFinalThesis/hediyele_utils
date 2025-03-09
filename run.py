import streamlit as st
import sys
import pandas as pd
from io import StringIO
from db_operations.dbop_data import DatabaseOperationsData 
from table_executor.table_executor_utils import TableExecutorUtil
from data_writer.write_data_from_csv_to_db import WriteDataToDbFromCSV
from data_writer.main_category_writer import MainCategoryWriter
from data_writer.product_features_writer import ProductFeatureWriter
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from selenium_utils.scrapper import BaseScraper
from constants import WEB_SITES

st.set_page_config(page_title="Hediyele - Product Management", page_icon="🎁", layout="centered")

st.sidebar.title("Hediyele - Product Management")
options = st.sidebar.radio(
    "Select an action:",
    [
        "Add Product",
        "Add Product Manually",
        "Delete Product",
        "Bulk Add Products",
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

                # st.write("[3/4] Writing main categories...")
                # main_category_writer = MainCategoryWriter()
                # main_category_writer.write_main_categories()
                # st.success("Main categories written successfully!")

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
    
    if "product_data" not in st.session_state:
        st.session_state.product_data = {}

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
    price = st.number_input("Price", value=product_data.get("Price", ""), key="price")
    description = st.text_area("Description", value=product_data.get("Description", ""), key="description")
    rating = st.text_input("Rating", value=product_data.get("Rating", ""), key="rating")

    if st.button("Add Product"):
        if all([product_name, link, description, category_name, rating, price]):
            db_operations = DatabaseOperationsData()
            category_id = db_operations.add_category_if_not_exists(category_name)
            success = db_operations.add_product_to_database(product_name, category_id, link, price, description, rating)

            main_category_writer = MainCategoryWriter()
            main_category_writer.write_main_categories()

            product_feature_writer = ProductFeatureWriter()
            product_feature_writer.update_product_features()

            st.success(f"Product '{product_name}' has been successfully added!")
        else:
            st.error("Please fill in all the fields.")

elif options == "Bulk Add Products":
    st.title("Bulk Add Products")
    site_option = st.selectbox("Select Site", list(WEB_SITES.keys()))
    bulk_links = st.text_area("Enter Product Links", placeholder="Enter one product link per line")
    bulk_fetch_button = st.button("Fetch Bulk Products")
    bulk_products = []
    if bulk_fetch_button and bulk_links:
        links = [l.strip() for l in bulk_links.splitlines() if l.strip()]
        scraper_class = WEB_SITES.get(site_option)
        if scraper_class:
            scraper = scraper_class()
            for l in links:
                bulk_products.append(scraper.get_product_details(l))
            scraper.quit()
    if bulk_products:
        st.write("Fetched Products")
        df = pd.DataFrame(bulk_products)
        st.dataframe(df)
        if st.button("Add Bulk Products"):
            st.success("Bulk products added successfully!")

elif options == "Add Product Manually":
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
        df = pd.DataFrame(products, columns=["ID", "Category", "Main Category", "Link", "Name", "Price", "Rating"])
        gb = GridOptionsBuilder.from_dataframe(df)
        
        for col in df.columns:
            gb.configure_column(col, width=150)
            
        gb.configure_default_column(filter=True, sortable=True)
        
        gb.configure_selection("multiple", use_checkbox=True, pre_selected_rows=[])
        grid_options = gb.build()

        full_screen = st.checkbox("Full screen view")
        grid_height = 500 if full_screen else 300

        grid_response = AgGrid(
            df,
            gridOptions=grid_options,
            update_mode=GridUpdateMode.SELECTION_CHANGED,
            height=grid_height,
            width='100%',
            allow_unsafe_jscode=True,
            fit_columns_on_grid_load=True
        )
        
        try:
            selected_rows = grid_response.get("selected_rows", [])
            if selected_rows is None:
                selected_rows = []
            elif isinstance(selected_rows, pd.DataFrame):
                selected_rows = selected_rows.to_dict('records')
        except Exception as e:
            st.error(f"Error processing selected rows: {e}")
            selected_rows = []
            
        if len(selected_rows) > 0:
            if st.button("Delete selected products"):
                try:
                    for row in selected_rows:
                        success = db_operations.delete_product_from_database(row["ID"])
                        if success:
                            st.success(f"Product {row['Name']} deleted")
                        else:
                            st.error(f"Product {row['Name']} could not be deleted")
                    st.experimental_rerun()  # Sayfayı yenile
                except Exception as e:
                    st.error(f"Error during deletion: {e}")
        else:
            st.info("No products selected.")
    else:
        st.write("No products found")

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
        gb = GridOptionsBuilder.from_dataframe(df)
        
        for col in df.columns:
            gb.configure_column(col, width=150)
            
        gb.configure_default_column(filter=True, sortable=True)
        
        grid_options = gb.build()
        
        full_screen = st.checkbox("Full screen view")
        grid_height = 500 if full_screen else 300
        
        grid_response = AgGrid(
            df,
            gridOptions=grid_options,
            update_mode=GridUpdateMode.NO_UPDATE,
            height=grid_height,
            width='100%',
            allow_unsafe_jscode=True,
            fit_columns_on_grid_load=True
        )
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


