import streamlit as st
import requests
import json
import firebase_admin
from firebase_admin import credentials, firestore
import re
from datetime import datetime, timezone
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env (for local use)
load_dotenv()

# Check if Firebase is already initialized
if not firebase_admin._apps:
    try:
        # 1️ Try .env first (Local)
        firebase_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
        if firebase_path:
            cred = credentials.Certificate(firebase_path)
        # 2️ Fallback to Streamlit Secrets (Cloud)
        elif "FIREBASE_CREDENTIALS" in st.secrets:  # Only runs on Cloud
            cred = credentials.Certificate(json.loads(st.secrets["FIREBASE_CREDENTIALS"]))
        else:
            raise ValueError("Firebase credentials missing in both .env and secrets")
        
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"🔥 Firebase init failed: {e}")
        st.stop()

# Get API Key (Works Locally & Cloud)
WEB_API_KEY = os.getenv("WEB_API_KEY") or st.secrets.get("WEB_API_KEY")
if not WEB_API_KEY:
    st.error("❌ WEB_API_KEY missing in both .env and secrets")
    st.stop()
    
# Initialize Firestore and get API key
db = firestore.client()
    
def app():
    try:
        reviews_df = st.session_state.reviews_df
        st.markdown(
            """
            <style>
            .block-container {
                padding-top: 0rem !important;
            }
            </style>
            """, 
            unsafe_allow_html=True
        )

        # Initialize error variables if they don't exist
        if 'login_errors' not in st.session_state:
            st.session_state.login_errors = {
                "email": "",
                "password": ""
            }
        # Initialize error variable for the login response
        if 'login_response_error' not in st.session_state:
            st.session_state.login_response_error = "" # stores error message for invalid credentials

        # Initialize error variable for the login response
        if 'login_success_response' not in st.session_state:
            st.session_state.login_success_response = False # stores error message for invalid credentials

        if 'password_recovery_error' not in st.session_state:
            st.session_state.password_recovery_error = ""
        if 'password_recovery_response' not in st.session_state:
            st.session_state.password_recovery_response = ""

        if 'user_data' not in st.session_state:   
            st.session_state.user_data = None   # holds user info, collected during signup

        # Initialize error variables if they don't exist
        if 'signup_errors' not in st.session_state:
            st.session_state.signup_errors = {
                "name": "",
                "email": "",
                "password": "",
                "confirm_password": "",
                "occupation": ""
            }
        # Initialize  error variable for sign up fails
        if 'signup_response_error' not in st.session_state:
            st.session_state.signup_response_error = "" # stores error message for failed signUp
        # Initialize session variable for successful signup
        if 'signup_successful' not in st.session_state:
            st.session_state.signup_successful = "" # stores message for successful signup

        if not st.session_state.logged_in:
            # Define a regex pattern for validating email addresses
            email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'

            # call back to handle login 
            def login_handler():
                # Clear previous errors
                st.session_state.login_errors = {"email": "", "password": ""}
                st.session_state.login_response_error = ""
                st.session_state.login_success_response = False

                # Retrieve form values from login form submission
                email = st.session_state["email_login"]
                password = st.session_state["password_login"]

                email = email.strip()
                password = password.strip()

                if not email:
                    st.session_state.login_errors['email'] = "Email cannot be empty"
                elif not re.match(email_pattern, email):
                    st.session_state.login_errors['email'] = "please enter a valid email address"
                elif not password:
                    st.session_state.login_errors['password'] = "Password cannot be empty"

                # Check if there are any errors
                if not any(st.session_state.login_errors.values()):
                    #st.write(email,password)
                    try:
                        #REST API for firebase Authentication
                        login_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={WEB_API_KEY}"
                        payload = json.dumps({
                            "email": email,
                            "password": password,
                            "returnSecureToken": True
                        })
                        response = requests.post(login_url, data=payload)
                        response_data = response.json()
                        #st.write("fine up to here")
                        #st.write(response_data)
                        #st.write("Session State:", st.session_state)
                        if "idToken" in response_data:
                            # Successful login, get the user token
                            # ✅ Retrieve user_id from Firestore using `firebase_uid`
                            user_ref = db.collection("users").document(response_data['localId'])
                            user_doc = user_ref.get()

                            if user_doc.exists:
                                user_data = user_doc.to_dict()
                            else: 
                                user_data = {}

                            # Fetch user account details from Firebase Auth
                            account_info_url = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={WEB_API_KEY}"
                            account_payload = json.dumps({"idToken": response_data["idToken"]})
                            account_response = requests.post(account_info_url, data=account_payload)
                            account_data = account_response.json()

                            if "users" in account_data:
                                created_at_timestamp = int(account_data["users"][0]["createdAt"]) / 1000  # Convert to seconds
                                created_at_date = datetime.fromtimestamp(created_at_timestamp, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
                                user_data["created_at"] = created_at_date  # Add creation date to user_data

                            st.session_state.logged_in = True
                            st.session_state.useremail = response_data["email"]
                            st.session_state.username = response_data["localId"]  # User's Firebase UID
                            st.session_state.user_role = user_data.get("role", "user")
                            st.session_state.user_data = user_data
                            st.session_state.login_success_response = True  # Flag to show message temporarily

                            # Clean up login-related session variables
                            del st.session_state.login_errors
                            del st.session_state.login_response_error
                            del st.session_state.password_recovery_error
                            del st.session_state.password_recovery_response
                            del st.session_state.email_login
                            del st.session_state.password_login
                            del st.session_state.signup_successful
                        else:
                            st.session_state.login_response_error ="Invalid Email or Password! Please enter valid email and password"
                    except requests.exceptions.ConnectionError:
                        # Handle network connection errors
                        st.session_state.login_response_error = "Unable to connect to the internet. Please check your connection and try again."
                    except Exception as e:
                        st.session_state.login_response_error = f"An error occured: {str(e)}"

            # firebase API to reset password by email
            def send_password_reset(email):
                reset_password_url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={WEB_API_KEY}"
                payload = json.dumps({
                    "requestType": "PASSWORD_RESET",
                    "email": email
                })
                response = requests.post(reset_password_url, data=payload)
                response_data = response.json()

                if "email" in response_data:
                    st.session_state.password_recovery_response = f"Password reset email sent to {email}. Please check your inbox."
                else:
                    st.session_state.password_recovery_error =" Error sending password reset email. Please check your email address."

            # call back function to handle forgotten password recovery
            def forgot_password_handler():
                # Clear previous errors
                st.session_state.login_errors["email"] = ""
                st.session_state.password_recovery_error = ""
                st.session_state.password_recovery_response = ""

                # Retrieve form values from login form submission
                email = st.session_state["email_login"]
                email = email.strip()

                # Forgot Password
                if not email:
                    st.session_state.login_errors['email'] = "Please enter your email to reset your password"
                elif not re.match(email_pattern, email):
                    st.session_state.login_errors['email'] = "please enter a valid email address"
                if not st.session_state.login_errors['email']:
                    send_password_reset(email)


            # call back function to handle form submission
            def submit_handler():
                # Clear previous errors
                st.session_state.signup_errors = {
                    "name": "",
                    "email": "",
                    "password": "",
                    "confirm_password": "",
                    "occupation": ""
                }
                st.session_state.signup_response_error = ""
                st.session_state.signup_successful = ""

                # Retrieve form values from session_state
                name = st.session_state["name_signup"].strip()
                email = st.session_state["email_signup"].strip()
                age = st.session_state["age_signup"]
                country = st.session_state["country_signup"].strip()
                city = st.session_state["city_signup"].strip()
                occupation = st.session_state["occupation_signup"].strip()
                phone_number = st.session_state["phone_signup"].strip()
                password = st.session_state["password_signup"].strip()
                confirm_password = st.session_state["confirm_password_signup"].strip()

                # Validate inputs
                if not name:
                    st.session_state.signup_errors["name"] = "Name cannot be empty."
                if not email:
                    st.session_state.signup_errors["email"] = "Email cannot be empty."
                elif not re.match(email_pattern, email):
                    st.session_state.signup_errors["email"] = "Please enter a valid email address."
                if not occupation:
                    st.session_state.signup_errors["occupation"] = "Occupation cannot be empty."
                if not password:
                    st.session_state.signup_errors["password"] = "Password cannot be empty."
                if password != confirm_password:
                    st.session_state.signup_errors["confirm_password"] = "Passwords do not match."
                if not any(st.session_state.signup_errors.values()):
                    try:
                        #REST API for firebase signup
                        signup_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={WEB_API_KEY}"
                        payload = json.dumps({
                                "email": email,
                                "password": password,
                                "returnSecureToken": True
                            })
                        response = requests.post(signup_url, data=payload)
                        response_data = response.json()
                        #st.write(response_data)
                        if "idToken" in response_data:
                            uid = response_data["localId"]  # Get the user Id
                            new_user_id = (reviews_df["user_id"].max()) + 1
                            # store other information in firestore
                            user_data = {
                                "user_id": int(new_user_id),
                                "name": name,
                                "email": email,
                                "age": age if age else None,
                                "country": country if country else "",
                                "city": city if city else "",
                                "occupation": occupation,
                                "phone": phone_number if phone_number else ""
                            }
                            db.collection("users").document(uid).set(user_data)
                            # ✅ Save `user_id` in session state (if needed later)
                            st.session_state.current_user_id = new_user_id
                            st.session_state.signup_successful = 'Account created successfully. Please login now.'

                            # Clean up signup-related session variables
                            del st.session_state.signup_errors
                            del st.session_state.signup_response_error
                            del st.session_state.name_signup
                            del st.session_state.email_signup
                            del st.session_state.age_signup
                            del st.session_state.country_signup
                            del st.session_state.city_signup
                            del st.session_state.phone_signup
                            del st.session_state.occupation_signup
                            del st.session_state.password_signup
                            del st.session_state.confirm_password_signup
                        else:
                            st.session_state.signup_response_error = "Sign-up failed. Please check the information and try again."
                    except requests.exceptions.ConnectionError:
                        # Handle network connection errors
                        st.session_state.signup_response_error = "Unable to connect to the internet. Please check your connection and try again."
                    except Exception as e:
                        st.session_state.signup_response_error = f"An error occurred: {str(e)}"

            log_col1,log_col2,log_col3 = st.columns([1, 2, 1])
            with log_col2:
                st.title("Welcome to Recipe Recommendation System.")
                login_tab, signup_tab = st.tabs(["Login", "Sign Up"])
                # with login tab
                with login_tab:
                    st.header("Login")
                    with st.form(key='login_form'):
                        # Create two columns for the email input and its error message
                        email_col1, email_col2 = st.columns([3, 1])  # Adjust the ratio for spacing
                        # Email input field and error message
                        with email_col1:
                            email = st.text_input("Email Address", placeholder="Enter your email", key="email_login", autocomplete='off') 
                        with email_col2:
                            if st.session_state.login_errors['email']:
                                st.error(st.session_state.login_errors['email'])
                        # Password input and error
                        password_col1, password_col2 = st.columns([3, 1])
                        with password_col1:
                            password = st.text_input("Password", type="password", placeholder="Enter your password", key="password_login")
                        with password_col2:
                            if st.session_state.login_errors["password"]:
                                st.error(st.session_state.login_errors["password"])

                        # Create columns for buttons
                        col1, col2 = st.columns([1,1])  # Two equally spaced columns    
                        with col1:
                            st.form_submit_button(label='Login', on_click=login_handler)
                        with col2:
                            st.form_submit_button(label='Forgot password', on_click=forgot_password_handler)

                    # Display success message on login
                    if st.session_state.login_success_response:
                        st.success("Login Successful.")

                    # Display login response error (invalid credentials) after the buttons
                    if st.session_state.login_response_error:
                        st.error(st.session_state.login_response_error)

                    # Display forgot password response
                    if st.session_state.password_recovery_response:
                        st.success(st.session_state.password_recovery_response)
                    if st.session_state.password_recovery_error:
                        st.error(st.session_state.password_recovery_error)
                # with sign up tab
                with signup_tab:
                    st.header("Sign Up")

                    # clear input fields after successful SignUp
                    if st.session_state.signup_successful:
                        st.session_state.password_signup = ""
                        st.session_state.confirm_password_signup = "" 

                    with st.form(key='signup_form', clear_on_submit=False):
                        # Create input fields for each piece of information
                        # Name input and error
                        name_col1, name_col2 = st.columns([3, 1])
                        with name_col1:
                            name = st.text_input("Name *", placeholder="Enter your Name", key="name_signup", autocomplete='off')
                        with name_col2:
                            if st.session_state.signup_errors["name"]:
                                st.error(st.session_state.signup_errors["name"])
                        # Email input and error
                        email_col1, email_col2 = st.columns([3, 1])
                        with email_col1:
                            email = st.text_input("Email Address *", placeholder="Enter your email address", key="email_signup", autocomplete='off')
                        with email_col2:
                            if st.session_state.signup_errors["email"]:
                                st.error(st.session_state.signup_errors["email"])

                        age = st.number_input("Age", min_value=0, max_value=120, placeholder="Enter your age", value=None, key="age_signup")
                        country = st.selectbox("Country", options=["","India", "United States", "Canada", "United Kingdom", "Other"], index=0, key="country_signup") # Default to empty option
                        city = st.text_input("City", placeholder="Enter the City you live", key="city_signup", autocomplete='off')
                        phone_number = st.text_input("Phone Number", placeholder="Enter your phone number", key="phone_signup", autocomplete='off')
                        # occupation input and error
                        occupation_col1, occupation_col2 = st.columns([3, 1])
                        with occupation_col1:
                            occupation = st.text_input("Occupation *", placeholder="Enter your Occupation", key="occupation_signup", autocomplete='off')
                        with occupation_col2:
                            if st.session_state.signup_errors["occupation"]:
                                st.error(st.session_state.signup_errors["occupation"])

                        # Password input and error
                        password_col1, password_col2 = st.columns([3, 1])
                        with password_col1:
                            password = st.text_input("Password *", type="password", placeholder="Enter your password", key="password_signup")
                        with password_col2:
                            if st.session_state.signup_errors["password"]:
                                st.error(st.session_state.signup_errors["password"])

                        # Confirm password input and error
                        confirm_password_col1, confirm_password_col2 = st.columns([3, 1])
                        with confirm_password_col1:
                            confirm_password = st.text_input("Confirm Password *", type="password", placeholder="Confirm your password", key="confirm_password_signup")
                        with confirm_password_col2:
                            if st.session_state.signup_errors["confirm_password"]:
                                st.error(st.session_state.signup_errors["confirm_password"])

                        st.form_submit_button(label='SignUp', on_click= submit_handler)
                    # if signed up
                    if st.session_state.signup_successful:
                        st.success(st.session_state.signup_successful)
                        st.balloons()

                        # Reset the signup_successful state to prevent re-triggering balloons
                        st.session_state.signup_successful = False
                    if st.session_state.signup_response_error:
                        st.error(st.session_state.signup_response_error)
    except Exception as e:
        st.error("Oops! Something went wrong.")

