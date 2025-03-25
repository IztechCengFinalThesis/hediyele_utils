import streamlit as st
import os

def app():
    st.title("Upload CSV Products")
    uploaded_file = st.file_uploader("Upload a CSV file", type=["xlsx"])

    if uploaded_file is not None:
        upload_folder = "data/"
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        file_path = os.path.join(upload_folder, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success("File uploaded successfully!")
