import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
from db_operations.dbop_price_tracking import DatabaseOperationsPriceTracking

def app():
    st.title("Price Charts")
    
    db_ops = DatabaseOperationsPriceTracking()
    
    products = db_ops.get_products_with_price_changes()
    
    if not products:
        st.info("No products with price changes found.")
        return
    
    product_options = {f"{name} ({site})": product_id for product_id, name, site in products}
    
    selected_product_label = st.selectbox(
        "Select a product to view price history:",
        options=list(product_options.keys())
    )
    
    if selected_product_label:
        selected_product_id = product_options[selected_product_label]
        price_history = db_ops.get_price_history(selected_product_id)
        
        if price_history:
            df = pd.DataFrame(price_history)
            df['date'] = pd.to_datetime(df['date'])
            
            df = df.sort_values('date')
            
            st.subheader(f"Price History for {selected_product_label}")
            
            chart = alt.Chart(df).mark_line(point=True).encode(
                x=alt.X('date:T', title='Date'),
                y=alt.Y('new_price:Q', title='Price'),
                tooltip=['date:T', 'new_price:Q']
            ).properties(
                height=400
            ).interactive()
            
            st.altair_chart(chart, use_container_width=True)
            
            all_prices = []
            all_prices.append(df.iloc[0]['old_price'])
            all_prices.extend(df['new_price'].tolist())
            
            st.subheader("Price Change History")
            
            display_df = df.copy()
            display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
            display_df = display_df.rename(columns={
                'date': 'Date',
                'old_price': 'Previous Price',
                'new_price': 'New Price'
            })
            
            display_df['Price Change'] = display_df['New Price'] - display_df['Previous Price']
            display_df['Change %'] = (display_df['Price Change'] / display_df['Previous Price'] * 100).round(2)
            
            display_df = display_df.sort_values('Date', ascending=False).reset_index(drop=True)
            
            def highlight_price_changes(val):
                if isinstance(val, (int, float)):
                    color = 'red' if val < 0 else 'green' if val > 0 else 'black'
                    return f'color: {color}'
                return ''
            
            styled_df = display_df.style.format({
                'Previous Price': '{:.2f}',
                'New Price': '{:.2f}',
                'Price Change': '{:.2f}',
                'Change %': '{:.2f}%'
            })
            
            for col in ['Price Change', 'Change %']:
                styled_df = styled_df.applymap(highlight_price_changes, subset=[col])
                
            st.dataframe(styled_df)
            
            st.subheader("Price Statistics")
            
            min_price = min(all_prices)
            max_price = max(all_prices)
            
            current_price = df.iloc[-1]['new_price']
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Lowest Price", f"{min_price:.2f}")
            with col2:
                st.metric("Highest Price", f"{max_price:.2f}")
            with col3:
                st.metric("Current Price", f"{current_price:.2f}")
                
            if len(all_prices) > 1:
                first_price = all_prices[0]
                price_change = current_price - first_price
                percentage_change = (price_change / first_price) * 100
                
                st.subheader("Overall Price Change")
                col1, col2 = st.columns(2)
                with col1:
                    delta_color = "normal" if price_change == 0 else "inverse" if price_change < 0 else "normal"
                    st.metric(
                        "Price Change", 
                        f"{price_change:.2f}", 
                        f"{percentage_change:.2f}%",
                        delta_color=delta_color
                    )
                with col2:
                    st.metric("Starting Price", f"{first_price:.2f}")
        else:
            st.info("No price history available for this product.")
    
    db_ops.close()

