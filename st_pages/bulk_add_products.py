import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
from db_operations.dbop_data import DatabaseOperationsData
from data_writer.main_category_writer import MainCategoryWriter
from data_writer.product_features_writer import ProductFeatureWriter
from constants import WEB_SITES, AGE_GROUPS, GENDERS, SPECIAL_OCCASIONS, INTERESTS

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
    
    if "bulk_product_data_with_images" not in st.session_state:
        st.session_state.bulk_product_data_with_images = []
    if "bulk_product_data" not in st.session_state:
        st.session_state.bulk_product_data = []
    if "product_features" not in st.session_state:
        st.session_state.product_features = []
    if "current_step" not in st.session_state:
        st.session_state.current_step = "input"
    if "site_option" not in st.session_state:
        st.session_state.site_option = None

    if st.session_state.current_step == "input":
        site_option_selected = st.selectbox("Select Site", list(WEB_SITES.keys()), key="bulk_site_select")
        st.session_state.site_option = site_option_selected

        bulk_links = st.text_area("Enter Product Links", placeholder="Enter one product link per line")

        if st.button("Fetch Bulk Products"):
            if bulk_links.strip():
                links = [l.strip() for l in bulk_links.splitlines() if l.strip()]
                scraper_class = WEB_SITES.get(st.session_state.site_option)

                if scraper_class:
                    scraper = scraper_class()
                    fetched_products_raw = []
                    
                    with st.spinner(f"Fetching {len(links)} products..."):
                        for i, l in enumerate(links):
                            st.write(f"Fetching {i+1}/{len(links)}: {l}")
                            product_details = scraper.get_product_details(l)
                            if product_details:
                                fetched_products_raw.append(product_details)
                    
                    scraper.quit()
                    
                    if fetched_products_raw:
                        st.session_state.bulk_product_data_with_images = fetched_products_raw
                        display_data = []
                        for p in fetched_products_raw:
                            item = {k: v for k, v in p.items() if k != 'Image'}
                            item['Site'] = st.session_state.site_option
                            display_data.append(item)
                        st.session_state.bulk_product_data = display_data
                        st.success(f"Fetched {len(fetched_products_raw)} products successfully!")
                    else:
                        st.warning("No products were fetched. Please check the links.")
            else:
                st.error("Please enter at least one product link.")

        if st.session_state.bulk_product_data:
            st.subheader("Review Product Data (Images not shown in grid)")
            df = pd.DataFrame(st.session_state.bulk_product_data)
            edited_df = st.data_editor(df, num_rows="dynamic")

            if st.button("Calculate Features"):
                feature_writer = ProductFeatureWriter()
                all_features_data = []
                
                for idx, row in edited_df.iterrows():
                    raw_product = next((p for p in st.session_state.bulk_product_data_with_images if p['Link'] == row['Link']), None)
                    image_bytes = raw_product['Image'] if raw_product else None

                    product_info = {
                        "product_name": row["Product Name"],
                        "category_name": row["Category"],
                        "description": row["Description"]
                    }
                    features = feature_writer.calculate_product_features(product_info)
                    
                    product_full_data = {
                        "Product Name": row["Product Name"],
                        "Category": row["Category"],
                        "Link": row["Link"],
                        "Price": row["Price"],
                        "Description": row["Description"],
                        "Rating": row["Rating"],
                        "Image": image_bytes,
                        "Site": row["Site"],
                        **features
                    }
                    all_features_data.append(product_full_data)
                
                st.session_state.product_features = all_features_data
                st.session_state.current_step = "review"
                st.rerun()

    elif st.session_state.current_step == "review":
        st.subheader("Review Product Features (Images not shown in grid)")
        
        if st.session_state.product_features:
            df_display_cols = [col for col in st.session_state.product_features[0].keys() if col not in ['Image', 'Site']]
            df_display = pd.DataFrame([{k: p[k] for k in df_display_cols} for p in st.session_state.product_features])
            
            tabs = st.tabs(["Age Groups", "Gender", "Special Occasions", "Interests"])
            
            with tabs[0]:
                df_display = create_feature_grid(df_display, AGE_GROUPS, "Age Groups")
            
            with tabs[1]:
                df_display = create_feature_grid(df_display, GENDERS, "Gender")
            
            with tabs[2]:
                df_display = create_feature_grid(df_display, SPECIAL_OCCASIONS, "Special Occasions")
            
            with tabs[3]:
                df_display = create_feature_grid(df_display, INTERESTS, "Interests")
            
            col1, col2 = st.columns(2)
            
            if col1.button("Back to Edit"):
                st.session_state.current_step = "input"
                st.rerun()

            if col2.button("Confirm and Save"):
                db_operations = DatabaseOperationsData()
                feature_writer = ProductFeatureWriter()
                main_category_writer = MainCategoryWriter()
                
                success_count = 0
                error_count = 0
                
                with st.spinner(f"Saving {len(st.session_state.product_features)} products..."):
                    for i, product_data_with_features in enumerate(st.session_state.product_features):
                        st.write(f"Processing {i+1}/{len(st.session_state.product_features)}: {product_data_with_features.get('Product Name', 'N/A')}")

                        edited_feature_row = df_display[df_display['Link'] == product_data_with_features['Link']].iloc[0]

                        category_id = db_operations.add_category_if_not_exists(edited_feature_row["Category"])
                        
                        if not category_id:
                            st.warning(f"Skipping product due to category error: {edited_feature_row['Product Name']}")
                            error_count += 1
                            continue

                        new_product_id = db_operations.add_product_to_database(
                            edited_feature_row["Product Name"],
                            category_id,
                            edited_feature_row["Link"],
                            edited_feature_row["Price"],
                            edited_feature_row["Description"],
                            edited_feature_row["Rating"],
                            product_data_with_features["Site"]
                        )
                        
                        if new_product_id:
                            current_features = {
                                key: edited_feature_row.get(display_name, product_data_with_features.get(key))
                                for feature_group in [AGE_GROUPS, GENDERS, SPECIAL_OCCASIONS, INTERESTS]
                                for key, display_name in feature_group.items()
                            }
                            
                            feature_writer.save_product_features(new_product_id, current_features)

                            image_bytes = product_data_with_features.get("Image")
                            if image_bytes:
                                img_success = db_operations.add_product_image(new_product_id, image_bytes)
                                if not img_success:
                                    st.warning(f"Saved product {edited_feature_row['Product Name']}, but failed to save image.")
                            
                            success_count += 1
                        else:
                            st.warning(f"Skipping product (already exists or DB error): {edited_feature_row['Product Name']}")
                            error_count += 1

                if success_count > 0:
                    main_category_writer.write_main_categories()
                    st.success(f"Successfully added {success_count} products!")
                    if error_count > 0:
                        st.warning(f"{error_count} products were skipped (check warnings above).")
                    st.session_state.current_step = "input"
                    st.session_state.bulk_product_data = []
                    st.session_state.product_features = []
                    st.session_state.bulk_product_data_with_images = []
                    st.rerun()
                else:
                    st.error(f"No products were added successfully. {error_count} products were skipped.")
