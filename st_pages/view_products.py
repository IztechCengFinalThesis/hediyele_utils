import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from db_operations.dbop_data import DatabaseOperationsData

def app():
    st.title("View Products")
    
    db_operations = DatabaseOperationsData()
    total_products = db_operations.get_total_product_count()
    products_per_page = st.number_input("Products per page", min_value=5, max_value=5000, value=1000, step=5)
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
        
        AgGrid(
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
