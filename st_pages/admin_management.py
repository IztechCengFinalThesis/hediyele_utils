import streamlit as st
import datetime
from db_operations.dbop_auth import DatabaseOperationsAuth

def app():
    st.title("Admin User Management")
    
    # Check if authenticated
    if "authenticated" not in st.session_state or not st.session_state.authenticated:
        st.error("Please login to access this page")
        return
    
    db_auth = DatabaseOperationsAuth()
    
    # Create tabs for different operations
    tab1, tab2 = st.tabs(["Create Admin User", "Manage Admin Users"])
    
    with tab1:
        st.subheader("Create New Admin User")
        
        with st.form("create_admin_form"):
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            create_btn = st.form_submit_button("Create User")
            
            if create_btn:
                if not new_username or not new_password:
                    st.error("Both username and password are required")
                elif new_password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    if db_auth.create_admin_user(new_username, new_password):
                        st.success(f"Admin user '{new_username}' created successfully")
                    else:
                        st.error("Failed to create admin user. Username might already exist.")
    
    with tab2:
        st.subheader("Manage Existing Admin Users")
        
        # Display all admin users
        users = db_auth.get_all_admin_users()
        if users:
            user_data = []
            for user in users:
                user_id, username, created_at = user
                if isinstance(created_at, datetime.datetime):
                    created_at_formatted = created_at.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    created_at_formatted = str(created_at)
                    
                user_data.append({
                    "ID": user_id,
                    "Username": username,
                    "Created At": created_at_formatted,
                })
            
            st.table(user_data)
            
            # Delete user form
            with st.form("delete_user_form"):
                st.warning("Danger Zone: Delete Admin User")
                user_to_delete = st.selectbox(
                    "Select User to Delete",
                    options=[user["Username"] for user in user_data],
                    key="user_to_delete"
                )
                user_id_to_delete = next((user["ID"] for user in user_data if user["Username"] == user_to_delete), None)
                
                delete_btn = st.form_submit_button("Delete User")
                if delete_btn and user_id_to_delete:
                    if db_auth.delete_admin_user(user_id_to_delete):
                        st.success(f"User '{user_to_delete}' deleted successfully")
                        st.rerun()
                    else:
                        st.error("Failed to delete user")
        else:
            st.info("No admin users found")
    
    db_auth.close() 