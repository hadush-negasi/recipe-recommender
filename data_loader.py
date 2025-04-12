import streamlit as st
import pandas as pd

@st.cache_data
def load_data(path, modification_time, columns=None):
    """
    Generalized function to load a dataset from the specified path.
    Supports multiple file formats.
    """
    print(f"Loading data from {path} (modification time: {modification_time})")
    if path.endswith('.feather'):
        if columns:
            return pd.read_feather(path,columns=columns)
        else:
            return pd.read_feather(path)
    elif path.endswith('.pkl'):
        return pd.read_pickle(path)
    else:
        raise ValueError("Unsupported file format. Supported formats: .feather, .pkl")
    
@st.cache_data
def load_user_predictions(user_id, path, modification_time):
    """
    Load only the specific user's predictions from the Feather file
    """
    if user_id is None:
        return None
    else:
        print(f"Loading predictions for user {user_id} from {path} (modification time: {modification_time})")
        
        if path.endswith('.feather'):    
            # Read just the user_id column first to find the row index
            user_ids = pd.read_feather(path, columns=['user_id'])
            row_index = user_ids[user_ids['user_id'] == user_id].index
    
            if len(row_index) == 0:
                print(f"No predictions found for user {user_id}")
                return None
            else:
                # Now read just that specific row
                return pd.read_feather(path).iloc[row_index]
