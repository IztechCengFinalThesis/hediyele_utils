import streamlit as st

st.set_page_config(page_title="Hediyele - Product Management", page_icon="🎁", layout="centered")

# Initialize session state for authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Display login page if not authenticated
if not st.session_state.authenticated:
    from st_pages.login import app as login_app
    login_app()
else:
    # Show sidebar and options only when authenticated
    st.sidebar.title("Hediyele - Product Management")
    
    # Add logout button in sidebar
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()
    
    # Show username in sidebar
    if "username" in st.session_state:
        st.sidebar.success(f"Logged in as: {st.session_state.username}")
    
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
            "Price Charts",
            "Admin Management",
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
        
    elif options == "Admin Management":
        from st_pages.admin_management import app as admin_management_app
        admin_management_app()
