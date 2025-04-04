# styles.py
import streamlit as st

def apply_styles():
    # Modern, nature-inspired color scheme
    st.markdown(
        """
        <style>
        /* Global background with subtle texture */
        .stApp {
            background-color: #f8f9fa;
            background-image: radial-gradient(#e9ecef 1px, transparent 1px);
            background-size: 20px 20px;
        }
        
        /* Text colors */
        .css-1v3fvcr, .css-2trqyj, .css-16huue1 {
            color: #2b2d42; /* Dark blue-gray for text */
        }
        
        /* Primary accent color (used for buttons, highlights) */
        :root {
            --primary: #588157; /* Nature green */
            --primary-hover: #3a5a40; /* Darker green */
            --secondary: #dda15e; /* Warm accent */
        }
        
        /* Input fields styling */
        .stTextInput>div>div>input, 
        .stTextArea>div>div>textarea,
        .stSelectbox>div>div>select {
            background-color: #ffffff;
            border: 1px solid #ced4da;
            border-radius: 8px;
            padding: 10px;
        }
        
        /* Button styling */
        .stButton button {
            background-color: var(--primary);
            color: white;
            border-radius: 8px;
            border: none;
            padding: 0.5rem 1rem;
            font-weight: 500;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        /* Button hover effect */
        .stButton button:hover {
            background-color: var(--primary-hover);
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        
        /* Secondary button styling */
        .stButton button[kind="secondary"] {
            background-color: white;
            color: var(--primary);
            border: 1px solid var(--primary);
        }
        
        /* Cards and containers */
        .stCard, .css-1aumxhk {
            background-color: white;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            padding: 1.5rem;
            border: 1px solid #e9ecef;
        }
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: white;
            border-right: 1px solid #e9ecef;
        }
        
        /* Title and Header Styling */
        h1 {
            color: #344e41; /* Dark green */
            font-weight: 700;
        }
        
        h2 {
            color: #588157; /* Primary green */
            font-weight: 600;
        }
        
        /* Success messages */
        .stAlert .st-ae {
            background-color: #d1e7dd;
        }
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
        }
        ::-webkit-scrollbar-thumb {
            background: var(--primary);
            border-radius: 4px;
        }
        
        /* Table styling */
        .stTable {
            border-radius: 8px;
            overflow: hidden;
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
        
        .stTabs [data-baseweb="tab"] {
            background: white;
            border-radius: 8px 8px 0 0;
            padding: 0.5rem 1rem;
            transition: all 0.3s ease;
        }
        
        .stTabs [aria-selected="true"] {
            background: var(--primary);
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True
    )