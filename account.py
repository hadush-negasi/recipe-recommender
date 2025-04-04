import streamlit as st
from streamlit_extras.card import card
from streamlit_extras.stylable_container import stylable_container
import firebase_admin
from firebase_admin import firestore, credentials
from datetime import datetime
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

# Check if Firebase is already initialized
if not firebase_admin._apps:
    # Initialize Firebase once if it hasn't been initialized
    cred = credentials.Certificate(os.getenv("FIREBASE_CREDENTIALS_PATH"))
    firebase_admin.initialize_app(cred)
    
db = firestore.client()

def logout_callback():
    st.session_state.clear()
    st.success("You have been logged out successfully!")

def get_user_favorites_count(user_id):
    """Count the number of favorite recipes for a user from reviews_df"""
    if 'reviews_df' not in st.session_state:
        return 0
    
    try:
        # Assuming reviews_df has columns: 'user_id' and 'rating'
        # Count recipes with rating >= 4 as favorites
        user_reviews = st.session_state.reviews_df[
            (st.session_state.reviews_df['user_id'] == user_id) & 
            (st.session_state.reviews_df['rating'] >= 4)
        ]
        return len(user_reviews)
    except Exception as e:
        st.error(f"Error counting favorites: {e}")
        return 0

def update_user_profile(updated_data):
    """Update Firestore document for the currently logged-in user."""
    if "username" not in st.session_state:
        st.error("User is not logged in.")
        return False

    localId = st.session_state.username  # Firebase UID (Document ID in Firestore)

    try:
        user_ref = db.collection("users").document(localId)
        user_ref.update(updated_data)  # Update document fields
        #st.success("Profile updated successfully!")
        return True
    except Exception as e:
        st.error(f"Error updating profile: {e}")
        return False

def app():    
    # ---- Hero Section ----
    st.markdown(
        """
        <style>
        .hero-account {
            background: linear-gradient(135deg, #2e8b57 0%, #3aafa9 100%);
            padding: 2rem;
            border-radius: 15px;
            color: white;
            margin-bottom: 2rem;
        }
        .hero-account h1 {
            font-size: 2.5rem;
        }
        </style>
        <div class="hero-account">
            <h1>My Account</h1>
            <p>Manage your profile and preferences</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ---- Check Login Status ----
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        st.warning("🔒 Please log in to view your account details")
        return

    if "user_data" not in st.session_state or "username" not in st.session_state:
        st.error("⚠️ Could not load your profile information")
        return

    user_id = st.session_state.user_data.get('user_id')
    username = st.session_state.username  # Firebase localId
    
    # Get dynamic user data
    favorites_count = get_user_favorites_count(user_id)
    last_login = datetime.now().strftime("%b %d, %Y %I:%M %p")

    # ---- Profile Editing State ----
    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = False

    # Toggle edit mode
    def toggle_edit_mode():
        st.session_state.edit_mode = not st.session_state.edit_mode

    # Save edited profile
    def save_profile():
        updated_data = {
            'age': st.session_state.edit_age,
            'country': st.session_state.edit_country,
            'city': st.session_state.edit_city,
            'occupation': st.session_state.edit_occupation,
            'phone': st.session_state.edit_phone
        }
        if update_user_profile(updated_data):
            # Update session state
            st.session_state.user_data.update(updated_data)
            st.success("Profile updated successfully!")
            st.session_state.edit_mode = False
        

    cols = st.columns([1, 2])
    
    # Profile Card (Left Column)
    with cols[0]:
        with stylable_container(
            key="profile_card",
            css_styles="""
            {
                background-color: #ffffff;
                border-radius: 15px;
                padding: 2rem;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            """
        ):
            st.markdown(
                f"""
                <div style="text-align: center;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="80" height="80" fill="#2e8b57" class="bi bi-person-circle" viewBox="0 0 16 16">
                        <path d="M11 6a3 3 0 1 1-6 0 3 3 0 0 1 6 0z"/>
                        <path fill-rule="evenodd" d="M0 8a8 8 0 1 1 16 0A8 8 0 0 1 0 8zm8-7a7 7 0 0 0-5.468 11.37C3.242 11.226 4.805 10 8 10s4.757 1.225 5.468 2.37A7 7 0 0 0 8 1z"/>
                    </svg>
                    <h2 style="color: #2e8b57; margin-top: 1rem;">{st.session_state.user_data.get('name', 'User')}</h2>
                    <p style="color: #6c757d;">{st.session_state.user_data.get('email', '')}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Quick Stats
            st.markdown("---")
            stats_cols = st.columns(2)
            with stats_cols[0]:
                st.markdown("**👤 Member Since**")
                st.caption(st.session_state.user_data.get("created_at", ""))
            with stats_cols[1]:
                st.markdown("**⭐ Favorites**")
                st.caption(f"{favorites_count} recipes")

    # Detailed Information (Right Column)
    with cols[1]:
        with stylable_container(
            key="details_card",
            css_styles="""
            {
                background-color: #ffffff;
                border-radius: 15px;
                padding: 2rem;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                height: 100%;
            }
            """
        ):
            if not st.session_state.edit_mode:
                # View Mode
                st.markdown("### 📝 Profile Details")
                
                # Personal Info Section
                with st.expander("Personal Information", expanded=True):
                    info_cols = st.columns(2)
                    with info_cols[0]:
                        st.markdown(f"**Full Name**  \n{st.session_state.user_data.get('name', '')}")
                        st.markdown(f"**Email**  \n{st.session_state.user_data.get('email', '')}")
                        st.markdown(f"**Phone**  \n{st.session_state.user_data.get('phone', '')}")
                    with info_cols[1]:
                        st.markdown(f"**Age**  \n{st.session_state.user_data.get('age', '')}")
                        st.markdown(f"**Occupation**  \n{st.session_state.user_data.get('occupation', '')}")
                
                # Location Section
                with st.expander("Location"):
                    loc_cols = st.columns(2)
                    with loc_cols[0]:
                        st.markdown(f"**Country**  \n{st.session_state.user_data.get('country', '')}")
                    with loc_cols[1]:
                        st.markdown(f"**City**  \n{st.session_state.user_data.get('city', '')}")
                
                # Account Section
                with st.expander("Account Information"):
                    st.markdown(f"**User ID**  \n`{user_id}`")
                    st.markdown("**Account Status**  \nActive ✅")
                    st.markdown(f"**Last Login**  \n{last_login}")
                
                # Edit Button
                st.button("✏️ Edit Profile", on_click=toggle_edit_mode, type="secondary")
            
            else:
                # Edit Mode
                st.markdown("### ✏️ Edit Profile")
                
                with st.form("profile_form"):
                    # Personal Info
                    st.text_input("Full Name", key="edit_name", value=st.session_state.user_data.get('name', ''), disabled=True)
                    
                    cols = st.columns(2)
                    with cols[0]:
                        st.text_input("Age", key="edit_age", value=st.session_state.user_data.get('age', ''))
                    with cols[1]:
                        st.text_input("Phone", key="edit_phone", value=st.session_state.user_data.get('phone', ''))
                    
                    # Location
                    st.text_input("Country", key="edit_country", value=st.session_state.user_data.get('country', ''))
                    st.text_input("City", key="edit_city", value=st.session_state.user_data.get('city', ''))
                    
                    # Occupation
                    st.text_input("Occupation", key="edit_occupation", value=st.session_state.user_data.get('occupation', ''))
                    
                    # Form buttons
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.form_submit_button("💾 Save Changes", type="primary", on_click=save_profile)
                    with col2:
                        st.form_submit_button("❌ Cancel", on_click=toggle_edit_mode)

    # ---- Logout Section ----
    st.markdown("---")
    st.button("🚪 Sign Out", on_click=logout_callback, type="primary", use_container_width=True)

