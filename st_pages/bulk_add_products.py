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
                    failed_links = []
                    
                    with st.spinner(f"Fetching {len(links)} products..."):
                        for i, l in enumerate(links):
                            try:
                                st.write(f"Fetching {i+1}/{len(links)}: {l}")
                                product_details = scraper.get_product_details(l)
                                if product_details:
                                    fetched_products_raw.append(product_details)
                                else:
                                    failed_links.append((l, "No product details returned"))
                            except Exception as e:
                                failed_links.append((l, str(e)))
                                st.warning(f"Failed to fetch: {l} - Error: {str(e)}")
                                continue
                    
                    try:
                        scraper.quit()
                    except Exception:
                        pass
                    
                    if fetched_products_raw:
                        st.session_state.bulk_product_data_with_images = fetched_products_raw
                        display_data = []
                        for p in fetched_products_raw:
                            item = {k: v for k, v in p.items() if k != 'Image'}
                            item['Site'] = st.session_state.site_option
                            display_data.append(item)
                        st.session_state.bulk_product_data = display_data
                        st.success(f"Fetched {len(fetched_products_raw)} products successfully!")
                        
                        if failed_links:
                            st.warning(f"Failed to fetch {len(failed_links)} links.")
                            with st.expander("Show failed links"):
                                for link, error in failed_links:
                                    st.write(f"- {link} (Error: {error})")
                    else:
                        st.warning("No products were fetched successfully. Please check the links.")
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
                    try:
                        raw_product = next((p for p in st.session_state.bulk_product_data_with_images if p['Link'] == row['Link']), None)
                        image_bytes = raw_product['Image'] if raw_product and 'Image' in raw_product else None

                        # Make sure we have the required fields
                        if not all(k in row and pd.notna(row[k]) for k in ["Product Name", "Category"]):
                            st.warning(f"Skipping row {idx+1}: Missing required fields")
                            continue

                        # Get description with fallback to empty string
                        description = row["Description"] if "Description" in row and pd.notna(row["Description"]) else ""
                        
                        product_info = {
                            "product_name": row["Product Name"],
                            "category_name": row["Category"],
                            "description": description
                        }
                        
                        try:
                            features = feature_writer.calculate_product_features(product_info)
                        except Exception as e:
                            st.warning(f"Error scoring features for {row.get('Product Name', 'Unknown product')}: {str(e)}")
                            # Create empty features dictionary with zeros
                            features = {}
                            for feature_dict in [AGE_GROUPS, GENDERS, SPECIAL_OCCASIONS, INTERESTS]:
                                for key in feature_dict:
                                    features[key] = 0.0
                        
                        # Build product data with safe defaults
                        product_data = {
                            "Product Name": row.get("Product Name", ""),
                            "Category": row.get("Category", ""),
                            "Link": row.get("Link", ""),
                            "Price": row.get("Price", 0.0),
                            "Description": description,
                            "Rating": row.get("Rating", 0.0),
                            "Image": image_bytes,
                            "Site": row.get("Site", st.session_state.site_option),
                        }
                        
                        # Add all feature values
                        product_data.update(features)
                        
                        all_features_data.append(product_data)
                    except Exception as e:
                        st.warning(f"Error processing row {idx+1}: {str(e)}")
                
                if all_features_data:
                    st.session_state.product_features = all_features_data
                    st.session_state.current_step = "review"
                    st.rerun()
                else:
                    st.error("Could not calculate features for any products. Please check your data.")

    elif st.session_state.current_step == "review":
        st.subheader("Review Product Features (Images not shown in grid)")
        
        if st.session_state.product_features:
            # Get all possible columns from all products to avoid missing keys
            all_keys = set()
            for p in st.session_state.product_features:
                all_keys.update(p.keys())
            
            df_display_cols = [col for col in all_keys if col not in ['Image', 'Site']]
            
            # Make sure to use get() method with default value
            df_display = pd.DataFrame([{k: p.get(k, 0.0) for k in df_display_cols} for p in st.session_state.product_features])
            
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
                        try:
                            st.write(f"Processing {i+1}/{len(st.session_state.product_features)}: {product_data_with_features.get('Product Name', 'N/A')}")

                            # Find the row in display dataframe that matches this product's link
                            product_link = product_data_with_features.get('Link', '')
                            if not product_link:
                                st.warning(f"Skipping product {i+1} - missing link")
                                error_count += 1
                                continue
                                
                            matching_rows = df_display[df_display['Link'] == product_link]
                            if matching_rows.empty:
                                st.warning(f"Skipping product - cannot find matching display data: {product_data_with_features.get('Product Name', 'N/A')}")
                                error_count += 1
                                continue
                            
                            edited_feature_row = matching_rows.iloc[0]
                            
                            # Get required data with safe defaults
                            product_name = edited_feature_row.get("Product Name", product_data_with_features.get("Product Name", ""))
                            category = edited_feature_row.get("Category", product_data_with_features.get("Category", ""))
                            
                            # Check for missing essential data
                            if not product_name or pd.isna(product_name):
                                st.warning(f"Skipping product {i+1} - missing product name")
                                error_count += 1
                                continue
                                
                            if not category or pd.isna(category):
                                st.warning(f"Skipping product {i+1} - missing category")
                                error_count += 1
                                continue

                            category_id = db_operations.add_category_if_not_exists(category)
                            
                            if not category_id:
                                st.warning(f"Skipping product due to category error: {product_name}")
                                error_count += 1
                                continue

                            # Get other values with safe defaults
                            product_link = edited_feature_row.get("Link", product_data_with_features.get("Link", ""))
                            product_price = edited_feature_row.get("Price", product_data_with_features.get("Price", 0.0))
                            if pd.isna(product_price): product_price = 0.0
                                
                            product_desc = edited_feature_row.get("Description", product_data_with_features.get("Description", ""))
                            if pd.isna(product_desc): product_desc = ""
                                
                            product_rating = edited_feature_row.get("Rating", product_data_with_features.get("Rating", 0.0))
                            if pd.isna(product_rating): product_rating = 0.0
                                
                            product_site = product_data_with_features.get("Site", st.session_state.site_option)

                            new_product_id = db_operations.add_product_to_database(
                                product_name,
                                category_id,
                                product_link,
                                product_price,
                                product_desc,
                                product_rating,
                                product_site
                            )
                            
                            if new_product_id:
                                # Process features safely
                                current_features = {}
                                for feature_group in [AGE_GROUPS, GENDERS, SPECIAL_OCCASIONS, INTERESTS]:
                                    for key, display_name in feature_group.items():
                                        try:
                                            # First try to get from edited display data
                                            value = edited_feature_row.get(display_name, None)
                                            # If not found or NaN, try original data
                                            if value is None or pd.isna(value):
                                                value = product_data_with_features.get(key, 0.0)
                                            # Ensure it's a valid float
                                            value = float(value) if not pd.isna(value) else 0.0
                                        except (ValueError, TypeError):
                                            # Default to 0.0 if conversion fails
                                            value = 0.0
                                        current_features[key] = value
                                
                                feature_writer.save_product_features(new_product_id, current_features)

                                image_bytes = product_data_with_features.get("Image")
                                if image_bytes:
                                    img_success = db_operations.add_product_image(new_product_id, image_bytes)
                                    if not img_success:
                                        st.warning(f"Saved product {product_name}, but failed to save image.")
                                
                                success_count += 1
                            else:
                                st.warning(f"Skipping product (already exists or DB error): {product_name}")
                                error_count += 1
                        except Exception as e:
                            st.warning(f"Error processing product {i+1}: {str(e)}")
                            error_count += 1
                            continue

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
