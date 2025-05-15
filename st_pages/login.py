import streamlit as st
from db_operations.dbop_auth import DatabaseOperationsAuth

def app():
    st.title("Admin Login")
    
    # Check if already authenticated
    if "authenticated" in st.session_state and st.session_state.authenticated:
        st.success("You are already logged in!")
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.rerun()
        return
    
    # Create login form
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if not username or not password:
                st.error("Both username and password are required")
                return
            
            db_auth = DatabaseOperationsAuth()
            if db_auth.authenticate_user(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")
            db_auth.close()

    # Admin user management section (hidden behind authentication in admin_management.py)
    st.markdown("---")
    st.info("If you need access, please contact the system administrator.") 