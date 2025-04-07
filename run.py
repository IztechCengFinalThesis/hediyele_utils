import streamlit as st

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
        "Upload CSV Products",
        "Run Database Setup",
        "Price Changes",
        "Price Charts"
    ]
)

if options == "Run Database Setup":
    from st_pages.run_database_setup import app as run_database_setup_app
    run_database_setup_app()

elif options == "Upload CSV Products":
    from st_pages.upload_csv_products import app as upload_csv_products_app
    upload_csv_products_app()

elif options == "Add Product":
    from st_pages.add_product import app as add_product_app
    add_product_app()

elif options == "Bulk Add Products":
    from st_pages.bulk_add_products import app as bulk_add_products_app
    bulk_add_products_app()

elif options == "Add Product Manually":
    from st_pages.add_product_manually import app as add_product_manually_app
    add_product_manually_app()

elif options == "Delete Product":
    from st_pages.delete_product import app as delete_product_app
    delete_product_app()

elif options == "View Products":
    from st_pages.view_products import app as view_products_app
    view_products_app()

elif options == "Edit Main Categories":
    from st_pages.edit_main_categories import app as edit_main_categories_app
    edit_main_categories_app()

elif options == "Price Changes":
    from st_pages.price_changes import app as price_changes_app
    price_changes_app()

elif options == "Price Charts":
    from st_pages.price_charts import app as price_charts_app
    price_charts_app()
