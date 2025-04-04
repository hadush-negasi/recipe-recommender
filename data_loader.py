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