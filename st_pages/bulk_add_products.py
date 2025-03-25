import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
from db_operations.dbop_data import DatabaseOperationsData
from data_writer.main_category_writer import MainCategoryWriter
from data_writer.product_features_writer import ProductFeatureWriter
from constants import WEB_SITES, AGE_GROUPS, GENDERS, SPECIAL_OCCASIONS, INTERESTS, GRID_COLUMN_SETTINGS

def create_feature_grid(df, feature_dict, title):
    st.write(f"### {title}")
    
    display_cols = ["Product Name", "Category"] + list(feature_dict.keys())
    display_df = df[display_cols].copy()
    
    column_names = {k: v for k, v in feature_dict.items()}
    display_df = display_df.rename(columns=column_names)
    
    gb = GridOptionsBuilder.from_dataframe(display_df)
    
    gb.configure_default_column(
        resizable=True,
        sorteable=True,
        filterable=True,
        editable=True,
        wrapText=True,
        autoHeight=True,
        minWidth=150
    )
    
    gb.configure_column(
        "Product Name",
        editable=False,
        minWidth=300,
    )
    gb.configure_column(
        "Category",
        editable=False,
        minWidth=200,
    )
    
    for _, display in column_names.items():
        gb.configure_column(
            display,
            type=["numericColumn", "numberColumnFilter"],
            editable=True,
            minWidth=150
        )
    
    grid_options = gb.build()
    
    grid_response = AgGrid(
        display_df,
        gridOptions=grid_options,
        height=400,
        fit_columns_on_grid_load=True,
        allow_unsafe_jscode=True,
    )
    
    reverse_names = {v: k for k, v in column_names.items()}
    for display_name, original_name in reverse_names.items():
        df[original_name] = grid_response['data'][display_name]
    
    return df

def app():
    st.title("Bulk Add Products")
    
    if "bulk_product_data" not in st.session_state:
        st.session_state.bulk_product_data = []
    if "product_features" not in st.session_state:
        st.session_state.product_features = []
    if "current_step" not in st.session_state:
        st.session_state.current_step = "input"

    if st.session_state.current_step == "input":
        site_option = st.selectbox("Select Site", list(WEB_SITES.keys()))
        bulk_links = st.text_area("Enter Product Links", placeholder="Enter one product link per line")

        if st.button("Fetch Bulk Products"):
            if bulk_links.strip():
                links = [l.strip() for l in bulk_links.splitlines() if l.strip()]
                scraper_class = WEB_SITES.get(site_option)

                if scraper_class:
                    scraper = scraper_class()
                    fetched_products = []
                    
                    for l in links:
                        product_details = scraper.get_product_details(l)
                        if product_details:
                            fetched_products.append(product_details)
                    
                    scraper.quit()
                    
                    if fetched_products:
                        st.session_state.bulk_product_data = fetched_products
                        st.success(f"Fetched {len(fetched_products)} products successfully!")
                    else:
                        st.warning("No products were fetched. Please check the links.")
            else:
                st.error("Please enter at least one product link.")

        if st.session_state.bulk_product_data:
            st.subheader("Review Product Data")
            df = pd.DataFrame(st.session_state.bulk_product_data)
            edited_df = st.data_editor(df, num_rows="dynamic")

            if st.button("Calculate Features"):
                feature_writer = ProductFeatureWriter()
                all_features = []
                
                for _, row in edited_df.iterrows():
                    product_info = {
                        "product_name": row["Product Name"],
                        "category_name": row["Category"],
                        "description": row["Description"]
                    }
                    features = feature_writer.calculate_product_features(product_info)
                    product_features = {
                        "Product Name": row["Product Name"],
                        "Category": row["Category"],
                        "Link": row["Link"],
                        "Price": row["Price"],
                        "Description": row["Description"],
                        "Rating": row["Rating"],
                        **features
                    }
                    all_features.append(product_features)
                
                st.session_state.product_features = all_features
                st.session_state.current_step = "review"
                st.rerun()

    elif st.session_state.current_step == "review":
        st.subheader("Review Product Features")
        
        if st.session_state.product_features:
            df = pd.DataFrame(st.session_state.product_features)
            
            tabs = st.tabs(["Age Groups", "Gender", "Special Occasions", "Interests"])
            
            with tabs[0]:
                df = create_feature_grid(df, AGE_GROUPS, "Age Groups")
            
            with tabs[1]:
                df = create_feature_grid(df, GENDERS, "Gender")
            
            with tabs[2]:
                df = create_feature_grid(df, SPECIAL_OCCASIONS, "Special Occasions")
            
            with tabs[3]:
                df = create_feature_grid(df, INTERESTS, "Interests")
            
            col1, col2 = st.columns(2)
            
            if col1.button("Back to Edit"):
                st.session_state.current_step = "input"
                st.rerun()

            if col2.button("Confirm and Save"):
                db_operations = DatabaseOperationsData()
                feature_writer = ProductFeatureWriter()
                main_category_writer = MainCategoryWriter()
                
                success_count = 0
                
                for _, row in df.iterrows():
                    category_id = db_operations.add_category_if_not_exists(row["Category"])
                    
                    success = db_operations.add_product_to_database(
                        row["Product Name"],
                        category_id,
                        row["Link"],
                        row["Price"],
                        row["Description"],
                        row["Rating"]
                    )
                    
                    if success:
                        features = {
                            key: row[key] 
                            for features in [AGE_GROUPS, GENDERS, SPECIAL_OCCASIONS, INTERESTS]
                            for key in features
                        }
                        
                        feature_writer.save_product_features(
                            db_operations.last_inserted_id(),
                            features
                        )
                        success_count += 1
                
                if success_count > 0:
                    main_category_writer.write_main_categories()
                    st.success(f"Successfully added {success_count} products!")
                    st.session_state.current_step = "input"
                    st.session_state.bulk_product_data = []
                    st.session_state.product_features = []
                    st.rerun()
                else:
                    st.error("No products were added successfully.")
