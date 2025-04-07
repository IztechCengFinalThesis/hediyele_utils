import streamlit as st
import os
from data_writer.main_category_writer import MainCategoryWriter

def app():
    st.title("Edit Main Categories")
    
    categories_file = "main_categories.txt"
    
    def load_categories_text():
        if os.path.exists(categories_file):
            with open(categories_file, "r") as file:
                return file.read()
        return ""
    
    def save_categories(categories_text):
        with open(categories_file, "w") as file:
            file.write(categories_text)
    
    categories_text = load_categories_text()
    
    st.subheader("Edit Main Categories")
    st.warning("Add each main category on a separate line.")
    
    edited_categories = st.text_area("Edit categories below:", 
                                    value=categories_text, 
                                    height=400)
    
    if st.button("Save Changes"):
        save_categories(edited_categories)
        
        with st.spinner("Updating database with new categories..."):
            try:
                writer = MainCategoryWriter()
                writer.clear_all_categories()
                writer.write_main_categories()
                st.success("Categories saved successfully and database updated!")
            except Exception as e:
                st.error(f"Error updating database: {str(e)}")
