import streamlit as st
from price_tracking.price_tracking import PriceTracker

def app():
    st.title("Price Changes")
    if st.button("Start Price Tracking"):
        price_tracker = PriceTracker()
        stats = price_tracker.track_prices()
        st.write("### Price Tracking Results")
        st.write(f"Total products checked: {stats['total']}")
        st.write(f"Products with price changes: {stats['updated']}")
        st.write(f"Products with unchanged prices: {stats['unchanged']}")
        st.write(f"Failed checks: {stats['failed']}")
