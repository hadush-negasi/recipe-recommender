import streamlit as st
from streamlit_option_menu import option_menu
from data_loader import load_data, load_user_predictions
import os
import about, account, recipe_search, login, contact, home, admin, recipe_recommend
from styles import apply_styles
from recipe_display import view_recipe_callback
from footer import footer
# app configuration
st.set_page_config(
    page_title="Recipe Recommender", 
    page_icon="🍽️",  # Customize with your app's icon
    layout="wide",
    initial_sidebar_state="auto",
    )

# initialize session state for the dataframes
if "reviews_df" not in st.session_state:
    st.session_state.reviews_df = None
if "recipes_df" not in st.session_state:
    st.session_state.recipes_df = None
if "user_pred_df" not in st.session_state:
    st.session_state.user_pred_df = None
if "item_pred_df" not in st.session_state:
    st.session_state.item_pred_df = None

# Define the columns to load for recipes_df
columns_to_load = ['recipe_id', 'tags', 'name', 'minutes', 'n_steps', 'steps', 'description', 'ingredients', 'Images']

# Load datasets using the generalized function
with st.spinner("Loading datasets..."):
    try:
        #print("loading reviews_df in the main.py")
        reviews_mod_time = os.path.getmtime('Data/reviews_df.feather')
        recipes_mod_time = os.path.getmtime('Data/recipes_clean.feather')
        user_pred_time = os.path.getmtime('Data/user_pred.feather')
        item_pred_time = os.path.getmtime('Data/item_pred.feather')

        st.session_state.reviews_df = load_data('Data/reviews_df.feather', reviews_mod_time)
        st.session_state.recipes_df = load_data('Data/recipes_clean.feather', recipes_mod_time, columns=columns_to_load)
    except Exception as e:
        st.error("Failed to load data files. Please check your 'Data/' folder.")
        #st.exception(e)

# check if user is logged in
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False # default to not logged in
    st.session_state.user_role = None  # for role management(user or admin)

if "login_success_response" not in st.session_state:
    st.session_state.login_success_response = ""
if "signup_successful" not in st.session_state:
    st.session_state.signup_successful = ""

# initialize session state for page navigation
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"

# Custom CSS to hide the Streamlit menu bar
hide_menu_style = """
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {padding-top: 0px !important;}
    </style>
"""
# Inject the CSS into the app to hide top bar from streamlit
#st.markdown(hide_menu_style, unsafe_allow_html=True)

#if logged in, show the side bar with the option menu
if st.session_state.logged_in:
    
    #delete previous success session messages
    del st.session_state.login_success_response
    del st.session_state.signup_successful

    apply_styles()
    
    # Different menu for admin vs regular users
    if st.session_state.user_role == "admin":
        try:
            st.session_state.user_pred_df = load_data('Data/user_pred.feather', user_pred_time)
            st.session_state.item_pred_df = load_data('Data/item_pred.feather', item_pred_time)
            # Convert all columns (except 'user_id') to integers
            st.session_state.user_pred_df.columns = [
                int(col) if col != 'user_id' else col for col in st.session_state.user_pred_df.columns
            ]
            # Convert all columns (except 'user_id') to integers
            st.session_state.item_pred_df.columns = [
                int(col) if col != 'user_id' else col for col in st.session_state.item_pred_df.columns
            ]
        except Exception as e:
            st.error("Oops.. couldn't load data. Something happended. please check your 'Data/' folder")
        app = option_menu(
            menu_title=None,
            options=["Admin","recommendations", "Account"],
            icons=["shield","lightbulb", "person"],
            default_index=0,
            orientation="horizontal",
            styles= {
                "container": {
                    "padding": "5px",
                    "background-color": "#f9f9f9",
                    "border-bottom": "1px solid #e0e0e0",  # Subtle bottom border
                    "box-shadow": "0 2px 5px rgba(0,0,0,0.05)",  # Soft shadow
                    "margin-bottom": "10px"  # Space below navbar
                },
                "icon": {
                    "color": "#2e8b57",  # Changed to nature-themed green
                    "font-size": "18px",
                    "margin-right": "5px"  # Space between icon and text
                },
                "nav-link": {
                    "font-size": "16px",
                    "text-align": "center",
                    "margin": "5px",
                    "padding": "8px 12px",
                    "border-radius": "5px",
                    "color": "#495057",
                    "transition": "all 0.3s ease"
                },
                "nav-link:hover": {  # Hover effect
                    "background-color": "#e9ecef",
                    "color": "#2e8b57"
                },
                "nav-link-selected": {
                    "background-color": "#2e8b57",
                    "color": "white",
                    "font-weight": "500",
                    "box-shadow": "0 2px 5px rgba(46, 139, 87, 0.2)"
                }
            }
        )
        try:
            if app == "Admin":
                admin.app()
            elif app == "recommendations":
                recipe_recommend.app()
            elif app == "Account":
                account.app()
        except Exception as e:
            st.error("An unexpected error occured.")
    else:
        try:
            st.session_state.user_pred_df = load_user_predictions(st.session_state.user_data.get('user_id', None), 'Data/user_pred.feather', user_pred_time)
            st.session_state.item_pred_df = load_user_predictions(st.session_state.user_data.get('user_id', None), 'Data/item_pred.feather', item_pred_time)
            
            if st.session_state.user_pred_df is not None:
                # Convert all columns (except 'user_id') to integers
                st.session_state.user_pred_df.columns = [
                    int(col) if col != 'user_id' else col for col in st.session_state.user_pred_df.columns
                ]
            if st.session_state.item_pred_df is not None:
                # Convert all columns (except 'user_id') to integers
                st.session_state.item_pred_df.columns = [
                    int(col) if col != 'user_id' else col for col in st.session_state.item_pred_df.columns
                ]
        except Exception as e:
            st.error("Oops... couldn't load user prediction data. please check your 'Data/' folder")
            st.error(e)
        # Track previous page
        if 'previous_page' not in st.session_state:
            st.session_state.previous_page = None
        if "show_description" not in st.session_state:
            st.session_state.show_description = False
        if "selected_recipe" not in st.session_state:
            st.session_state.selected_recipe = None
    
        # Define the navigation menu with icons and styles
        app = option_menu(
            menu_title=None,  # No title
            options=["Home", "Search", "About Us", "Contact Us", "Account"],  # Menu items
            icons=["house", "search", "info-circle", "envelope", "person"],  # Icons for each menu item
            default_index=0,  # Default selected tab
            orientation="horizontal",  # Horizontal layout
            styles={  
                "container": {
                    "padding": "5px",
                    "background-color": "#f9f9f9",
                    "border-bottom": "1px solid #e0e0e0",  # Subtle bottom border
                    "box-shadow": "0 2px 5px rgba(0,0,0,0.05)",  # Soft shadow
                    "margin-bottom": "10px"  # Space below navbar
                },
                "icon": {
                    "color": "#2e8b57",  # Changed to nature-themed green
                    "font-size": "18px",
                    "margin-right": "5px"  # Space between icon and text
                },
                "nav-link": {
                    "font-size": "16px",
                    "text-align": "center",
                    "margin": "5px",
                    "padding": "8px 12px",
                    "border-radius": "5px",
                    "color": "#495057",
                    "transition": "all 0.3s ease"
                },
                "nav-link:hover": {  # Hover effect
                    "background-color": "#e9ecef",
                    "color": "#2e8b57"
                },
                "nav-link-selected": {
                    "background-color": "#2e8b57",
                    "color": "white",
                    "font-weight": "500",
                    "box-shadow": "0 2px 5px rgba(46, 139, 87, 0.2)"
                }
            }
        )
        try:
            # Detect page change
            if st.session_state.previous_page != app:
                view_recipe_callback(None, False)
                st.session_state.previous_page = app

            # navigate to the desired page
            if app == "Home":
                home.app()
            elif app == "Search":
                recipe_search.app()
            elif app == "Account":
                account.app()
            elif app== "About Us":
                about.app()
            elif app=="Contact Us":
                contact.app()
        except Exception as e:
            st.error("An unexpected error occured.")
    footer()
    
else:
    # if user is not logged in, show popular recipes and login/signup page
    apply_styles()
    try:
        # Define the navigation menu with icons and styles
        app = option_menu(
            menu_title=None,  # No title
            options=["Home", "About Us", "Login/SignUp"],  # Menu items
            icons=["house", "info-circle", "person"],  # Icons for each menu item
            default_index=0,  # Default selected tab
            orientation="horizontal",  # Horizontal layout
            styles={  
                "container": {
                    "padding": "5px",
                    "background-color": "#f9f9f9",
                    "border-bottom": "1px solid #e0e0e0",  # Subtle bottom border
                    "box-shadow": "0 2px 5px rgba(0,0,0,0.05)",  # Soft shadow
                    "margin-bottom": "10px"  # Space below navbar
                },
                "icon": {
                    "color": "#2e8b57",  # Changed to nature-themed green
                    "font-size": "18px",
                    "margin-right": "5px"  # Space between icon and text
                },
                "nav-link": {
                    "font-size": "16px",
                    "text-align": "center",
                    "margin": "5px",
                    "padding": "8px 12px",
                    "border-radius": "5px",
                    "color": "#495057",
                    "transition": "all 0.3s ease"
                },
                "nav-link:hover": {  # Hover effect
                    "background-color": "#e9ecef",
                    "color": "#2e8b57"
                },
                "nav-link-selected": {
                    "background-color": "#2e8b57",
                    "color": "white",
                    "font-weight": "500",
                    "box-shadow": "0 2px 5px rgba(46, 139, 87, 0.2)"
                }
            }
        )
        st.title(":green[Welcome to Recipe Recommender System].")
        st.subheader(":red[Please Login/signup to get more personalized recommendations].")
        try:
            # navigate to the desired page
            if app == "Home":
                home.app()
            elif app== "About Us":
                about.app()
            elif app=="Login/SignUp":
                login.app()
        except Exception as e:
            st.error("An unexpected error occured.")
        st.subheader(":blue[Please Login/signup to get more personalized recommendations].")
        footer()
    except Exception as e:
        st.error("Something went wrong. Please refresh the page or try again later.")
        st.exception(e)
