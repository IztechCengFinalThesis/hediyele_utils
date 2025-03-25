import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from db_operations.dbop_data import DatabaseOperationsData

def app():
    st.title("Delete Product")
    db_operations = DatabaseOperationsData()
    total_products = db_operations.get_total_product_count()
    products_per_page = st.number_input("Products per page", min_value=5, max_value=5000, value=10, step=5)
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
                    st.rerun() 
                except Exception as e:
                    st.error(f"Error during deletion: {e}")
        else:
            st.info("No products selected.")
    else:
        st.write("No products found")
