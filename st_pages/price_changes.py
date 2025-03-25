import streamlit as st
from price_tracking import price_tracking
def app():
    st.title("Price Changes")
    if st.button("Start Price Tracking"):
        stats = price_tracking.track_prices()
        st.write("### Price Tracking Results")
        st.write(f"Total products checked: {stats['total']}")
        st.write(f"Products with price changes: {stats['updated']}")
        st.write(f"Products with unchanged prices: {stats['unchanged']}")
        st.write(f"Failed checks: {stats['failed']}")
