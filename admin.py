import streamlit as st
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import mean_squared_error
import pandas as pd
import numpy as np
import os
from math import sqrt
import time
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import firebase_admin
from firebase_admin import credentials, firestore, auth
from datetime import datetime, timezone
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
    
# Initialize Firestore and get API key
db = firestore.client()

def format_firebase_timestamp(ms_timestamp):
    """Convert Firebase Auth timestamp (milliseconds) to human-readable format."""
    if ms_timestamp:
        return datetime.fromtimestamp(ms_timestamp / 1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    return None

# Function to fetch all users from Firebase Auth and Firestore
def get_all_users():
    try:
        # List all users from Firebase Auth
        auth_users = auth.list_users().iterate_all()
        
        user_list = []
        
        for auth_user in auth_users:
            # Get additional user data from Firestore
            user_doc = db.collection("users").document(auth_user.uid).get()
            
            user_data = {
                'uid': auth_user.uid,
                'email': auth_user.email,
                'created_at': auth_user.user_metadata.creation_timestamp,
                'last_login': auth_user.user_metadata.last_sign_in_timestamp,
            }
            
            # Add Firestore data if exists
            if user_doc.exists:
                firestore_data = user_doc.to_dict()
                user_data.update({
                    'user_id': firestore_data.get('user_id'),
                    'name': firestore_data.get('name'),
                    'age': firestore_data.get('age'),
                    'country': firestore_data.get('country'),
                    'city': firestore_data.get('city'),
                    'occupation': firestore_data.get('occupation'),
                    'phone': firestore_data.get('phone')
                })
            
            user_list.append(user_data)
        
        # Convert to DataFrame and format timestamps
        df = pd.DataFrame(user_list)
        if not df.empty:
            df['created_at'] = df['created_at'].apply(format_firebase_timestamp)
            df['last_login'] = df['last_login'].apply(format_firebase_timestamp)
        return df
        
    except Exception as e:
        st.error(f"Error fetching users: {e}")
        return pd.DataFrame()

# Function to delete user from Firebase Auth and Firestore
def delete_user(uid):
    try:
        # First delete from Firestore (if exists)
        user_ref = db.collection("users").document(uid)
        user_doc = user_ref.get()
        
        if user_doc.exists:
            # Get user_id before deleting (if you need it for reference)
            user_id = user_doc.to_dict().get('user_id')
            user_ref.delete()
        
        # Then delete from Firebase Auth
        auth.delete_user(uid)
        # Clear delete state
        st.session_state.confirm_delete = False
        st.session_state.user_to_delete = None
        
        return True
    except Exception as e:
        st.error(f"Error deleting user: {e}")
        return False

    
def RMSE(prediction, ground_truth, test_data):
    """
    Compute RMSE considering explicitly rated recipes, including those rated as zero.
    
    Args:
    - prediction (np.array): The predicted rating matrix (N users * M recipes).
    - ground_truth (np.array): The actual rating matrix (N users * M recipes).
    
    Returns:
    - float: RMSE value
    """
    # Extract user_id, recipe_id from test_data
    user_indices = test_data['user_id'].values
    recipe_indices = test_data['recipe_id'].values
    
    # Get the explicitly rated values (including zeros) from ground_truth and predictions
    pred_values = prediction[user_indices, recipe_indices]
    true_values = ground_truth[user_indices, recipe_indices]

    rmse = sqrt(mean_squared_error(pred_values, true_values))

    return rmse

def user_basedCF():
    start_time = time.time()
    reviews_df = st.session_state.reviews_df
    # Compute adjusted rating (modifies DataFrame in-place)
    mu = reviews_df['rating'].mean()
    reviews_df['user_mean'] = reviews_df['user_id'].map(reviews_df.groupby('user_id')['rating'].mean())
    reviews_df['recipe_mean'] = reviews_df['recipe_id'].map(reviews_df.groupby('recipe_id')['rating'].mean())
    reviews_df['adjusted_rating'] = reviews_df['rating'] - (reviews_df['user_mean'] + reviews_df['recipe_mean'] - mu)
    # Cleanup (in-place)
    reviews_df.drop(columns=['user_mean', 'recipe_mean'], inplace=True)
    st.write(reviews_df.head(3))

    # Split dataset into training and test dataset
    #start_time = time.time()  # Start timer
    # Ensure minimum 20 interactions before splitting
    reviews_filtered = reviews_df.groupby('user_id').filter(lambda x: len(x) >= 20)

    # Create stratified split
    splitter = StratifiedShuffleSplit(n_splits=1, test_size=0.2)

    # Assign stratified train-test indices
    train_indices, test_indices = next(splitter.split(reviews_filtered, reviews_filtered['user_id']))

    # Create train and test sets
    train_data = reviews_filtered.iloc[train_indices]
    test_data = reviews_filtered.iloc[test_indices]

    # Append users with < 20 interactions entirely to train_data
    train_data = pd.concat([train_data, reviews_df[~reviews_df['user_id'].isin(reviews_filtered['user_id'])]])
    st.write(train_data.head(5))
    #end_time = time.time()  # End timer
    #print(f"Train-test split took {end_time - start_time:.4f} seconds")
    # Display results
    #print(f"Train size: {train_data.shape[0]}, Test size: {test_data.shape[0]}")

    # fill the user-item interaction with the baseline adjusted rating
    n_users = reviews_df['user_id'].nunique()
    n_items = reviews_df['recipe_id'].nunique()
    train_data_matrix = np.zeros((n_users, n_items))
    for row in train_data.itertuples():
        train_data_matrix[row[1], row[2]] = row[4]
    #print(train_data_matrix.shape)

    # test data matrix filled with the adjusted ratings
    test_data_matrix = np.zeros((n_users, n_items))
    for row in test_data.itertuples():
        test_data_matrix[row[1], row[2]] = row[4]
    #print(test_data_matrix.shape)

    # Compute centered cosine similarity (user-user similarity)
    user_similarity = cosine_similarity(train_data_matrix)
    #print(user_similarity.shape)
   # Compute centered cosine similarity (item-item similarity)
    item_similarity = cosine_similarity(train_data_matrix.T)
    #print(item_similarity1.shape)

    # User-based collaborative filtering; precict rating 
    baseline_centered_user_pred = user_similarity.dot(train_data_matrix) / np.array([np.abs(user_similarity).sum(axis=1)]).T
    #print(baseline_centered_user_pred.shape)

    # item-based collaborative filtering, prediction of ratings
    baseline_centered_item_pred = train_data_matrix.dot(item_similarity) / np.array([np.abs(item_similarity).sum(axis=1)])
    #print(baseline_centered_item_pred.shape)

    # calculate the rmse for user-based cf
    user_RMSE_baseline_centered = RMSE(baseline_centered_user_pred, test_data_matrix, test_data)
    item_RMSE_baseline_centered = RMSE(baseline_centered_item_pred, test_data_matrix, test_data)

    # change it to dataframe for saving to external file
    user_pred_df = pd.DataFrame(baseline_centered_user_pred, columns = list(range(n_items)))
    user_pred_df.insert(0, 'user_id', list(range(n_users)))
    item_pred_df = pd.DataFrame(baseline_centered_item_pred, columns = list(range(n_items)))
    item_pred_df.insert(0, 'user_id', list(range(n_users)))

    # Create the folder if it doesn't exist
    folder_path = "Data"
    os.makedirs(folder_path, exist_ok=True)

    # save as feather file type for faster reloading
    user_pred_df.to_feather(os.path.join(folder_path, "user_pred.feather"))
    item_pred_df.to_feather(os.path.join(folder_path, "item_pred.feather"))
    st.write("Model Retrained Successfully")
    st.write("user-based collaborative filtering using baseline-centering method: ", user_RMSE_baseline_centered)
    st.write("item-based collaborative filtering using baseline centering method", item_RMSE_baseline_centered)
    st.write(f"Time taken show selected recipe: {time.time() - start_time:.2f} seconds")



def app():
    st.header("Welcome Admin")
    # Clear delete state
    if "confirm_delete" not in st.session_state:
        st.session_state.confirm_delete = False
    if "user_to_delete" not in st.session_state:
        st.session_state.user_to_delete = None
    
    # Create tabs for different functionalities
    tab1, tab2, tab3 = st.tabs(["Data Exploration", "Model Management", "User Management"])
    
    with tab1:
        st.subheader("Dataset Explorer")
        
        # Dataset selection
        dataset = st.selectbox(
            "Choose Dataset to Explore",
            options=["Recipes", "Reviews", "User Predictions", "Item Predictions"],
            index=0
        )
        
        # Load corresponding dataframe
        if dataset == "Recipes":
            df = st.session_state.recipes_df
        elif dataset == "Reviews":
            df = st.session_state.reviews_df.copy()
        elif dataset == "User Predictions":
            df = st.session_state.user_pred_df
            df.columns = df.columns.astype(str)  # Convert integer columns to strings
        elif dataset == "Item Predictions":
            df = st.session_state.item_pred_df
            df.columns = df.columns.astype(str)  # Convert integer columns to strings
        # Configure AgGrid options based on dataset
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_pagination(paginationAutoPageSize=True)
        gb.configure_side_bar()
        # Set default column width
        #gb.configure_default_column(width=200)

        # Special handling for tags column in Recipes
        if dataset == "Recipes":
            # Configure wide columns
            gb.configure_column("tags", width=150, wrapText=True, autoHeight=True)
            gb.configure_column("name", width=200, wrapText=True)
            gb.configure_column("description", width=150, wrapText=True)
            gb.configure_column("ingredients", width=150, wrapText=True)
            gb.configure_column("steps", width=150, wrapText=True)
            gb.configure_column("Images", width=150)
    
            # Pin important columns to the left
            gb.configure_columns(['recipe_id','name'], pinned='left')
        
        # Enable editing only for Recipes and Reviews
        if dataset == "Reviews":
            gb.configure_default_column(editable=True, groupable=True)
            st.warning("⚠️ You can edit cells directly in the table below")
        else:
            st.info("View-only mode for this dataset")
        
        gridOptions = gb.build()
        gridOptions['alwaysShowHorizontalScroll'] = True
        
        # Display the grid
        grid_response = AgGrid(
            df,
            gridOptions=gridOptions,
            update_mode=GridUpdateMode.MODEL_CHANGED,
            allow_unsafe_jscode=True,
            height=500,
            key=f"grid_{dataset}"  # Unique key for each dataset
        )
        
        # Get the updated dataframe if changes were made
        if dataset == "Reviews":
            updated_df = grid_response['data']
            
            if not updated_df.equals(df):
                st.success("Changes detected!")
                
                if st.button("Save Changes"):
                    st.session_state.reviews_df = updated_df
                    st.success("Changes saved successfully!")
        
        # Add row functionality for Recipes and Reviews
        if dataset == "Reviews":
            st.subheader("Add New Record")
            cols = st.columns(len(df.columns))
            new_record = {}
            
            for i, col in enumerate(df.columns):
                with cols[i]:
                    new_record[col] = st.text_input(f"{col}", key=f"new_{col}")
            
            if st.button("Add Record"):
                if all(new_record.values()):  # Check all fields are filled
                    updated_df = pd.concat([updated_df, pd.DataFrame([new_record])], ignore_index=True)
                    if dataset == "Reviews":
                        st.session_state.reviews_df = updated_df
                    st.success("Record added successfully!")
                    st.experimental_rerun()
                else:
                    st.error("Please fill all fields")
        
    with tab2:
        st.subheader("Model Operations")
        retrain = st.button("Model Retrain")
        if retrain:
            user_basedCF()
    
    with tab3:
        st.subheader("Registered Users")
        
        # Get and display users
        users_df = get_all_users()
        
        if not users_df.empty:
            # Smaller AgGrid configuration
            gb = GridOptionsBuilder.from_dataframe(users_df)
            gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=5)
            gb.configure_side_bar()
            gb.configure_selection('single')
            
            # Custom column configuration
            gb.configure_column("uid", hide=True)
            gb.configure_column("email", width=200)
            gb.configure_column("name", width=150)
            gb.configure_column("user_id", width=80)
            gb.configure_column("created_at", width=150, headerName="Joined")
            gb.configure_column("last_login", width=150, headerName="Last Active")
            
            gridOptions = gb.build()
            
            # Display with smaller height
            grid_response = AgGrid(
                users_df,
                gridOptions=gridOptions,
                update_mode=GridUpdateMode.SELECTION_CHANGED,
                height=300,  # Reduced height
                fit_columns_on_grid_load=True,
                key="users_grid"
            )
            
            # Handle selection
            selected_rows = grid_response.get('selected_rows', [])
            # Proper way to check if any rows are selected
            if isinstance(selected_rows, pd.DataFrame):
                if not selected_rows.empty:
                    selected_user = selected_rows.iloc[0].to_dict()
            
                    # Cleaner user details display
                    with st.expander("👤 User Details", expanded=True):
                        cols = st.columns(3)
                        with cols[0]:
                            st.metric("Name", selected_user.get('name', 'N/A'))
                            st.write("**Email**")
                            # Use text area for long emails with copy button
                            email = selected_user.get('email', 'N/A')
                            st.code(email, language='text')
                           #st.metric("Email", selected_user.get('email', 'N/A'))
                            st.metric("Age", selected_user.get("age", "N/A"))

                        with cols[1]:
                            st.metric("User ID", selected_user.get('user_id', 'N/A'))
                            st.metric("Country", selected_user.get('country', 'N/A'))
                        with cols[2]:
                            st.metric("Occupation", selected_user.get('occupation', 'N/A'))
                            st.metric("Phone", selected_user.get("phone", "N/A"))

                        st.divider()
                        cols = st.columns(2)
                        with cols[0]:
                            st.write("**Account Created**")
                            st.code(selected_user.get('created_at', 'Unknown'))
                        with cols[1]:
                            st.write("**Last Activity**")
                            st.code(selected_user.get('last_login', 'Unknown'))

                        # Delete button with confirmation
                        st.divider()
                        if st.button("🗑️ Delete User", type="primary", key="delete_btn"):
                            st.session_state.confirm_delete = True
                            st.session_state.user_to_delete = selected_user
                            
        else:
            st.warning("No registered users found")

        # Confirmation modal (appears outside the main flow)
        if st.session_state.confirm_delete and st.session_state.user_to_delete:
            user = st.session_state.user_to_delete
            
            with st.container():
                st.error(f"You are about to permanently delete: {user['email']}")
                
                cols = st.columns(2)
                with cols[0]:
                    if st.button("✅ Confirm Delete", type="primary"):
                        if delete_user(user['uid']):
                            st.success(f"Deleted {user['email']}")
                            st.rerun()
                        else:
                            st.session_state.confirm_delete = False
                with cols[1]:
                    if st.button("❌ Cancel"):
                        st.session_state.confirm_delete = False
                        st.rerun()
    