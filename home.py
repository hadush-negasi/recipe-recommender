import streamlit as st
import pandas as pd
import numpy as np
from recipe_recommend import getRecommendations
from streamlit_extras.card import card
from streamlit_extras.grid import grid
from recipe_display import show_recipe_description, view_recipe_callback
from streamlit_extras.add_vertical_space import add_vertical_space

@st.cache_data
def get_recipes(personalized="Popular"):
    reviews_df = st.session_state.reviews_df
    recipes_df = st.session_state.recipes_df
    user_id = st.session_state.user_data.get('user_id')
    recommended_recipes = None
    # Calculate popularity metrics
    recipe_stats = reviews_df.groupby('recipe_id').agg(
        num_reviews=('rating', 'count'),
        avg_rating=('rating', 'mean')
    ).reset_index()
    recipe_stats['popularity_score'] = recipe_stats['avg_rating'] * np.log(recipe_stats['num_reviews'])
    recommended_recipes = pd.merge(recipe_stats, 
                               recipes_df, 
                               on='recipe_id', how='left')
    if personalized=="User-Based":
        recommendations = getRecommendations(user_id, "User-Based", 20)
        # Extract recipe IDs from the recommendations dictionary
        recommended_recipe_ids = list(recommendations.keys())
        # Ensure the order matches recommendations dict
        recommended_recipes = recommended_recipes.set_index('recipe_id').reindex(recommended_recipe_ids).reset_index()
    elif personalized=="Item-Based":
        recommendations = getRecommendations(user_id, "Item-Based", 20)
        # Extract recipe IDs from the recommendations dictionary
        recommended_recipe_ids = list(recommendations.keys())
        # Ensure the order matches recommendations dict
        recommended_recipes = recommended_recipes.set_index('recipe_id').reindex(recommended_recipe_ids).reset_index()
    elif personalized=="Popular":
        recipes_rated = reviews_df[reviews_df['user_id'] == user_id]['recipe_id'].unique()
        recommended_recipes = recommended_recipes[~recommended_recipes['recipe_id'].isin(recipes_rated)]
        recommended_recipes = recommended_recipes.sort_values(by='popularity_score', ascending=False).drop(columns=['popularity_score']).head(15)
    else:
        st.error("invalid recommedation type, please select, User-Based, Item-Based or Popular")
    return recommended_recipes

def search_recipe_callback():
    st.session_state.current_page = "recipe_search"

def show_recipes(recommended_recipes):
    # Create a grid of boxes (3 columns)
    cols = st.columns(3)  # Adjust the number of columns as needed
    
    # Split the recipes into groups for each column
    num_recipes = len(recommended_recipes)
    recipes_per_col = (num_recipes + len(cols) - 1) // len(cols)  # Round up

    # Default placeholder image (can be a local file or URL)
    DEFAULT_IMAGE = "https://via.placeholder.com/300x200?text=No+Image+Available"
    
    for col_index, col in enumerate(cols):
        with col:
            # Calculate the start and end index for this column
            start_index = col_index * recipes_per_col
            end_index = min(start_index + recipes_per_col, num_recipes)
            
            # Display recipes in this column
            for index in range(start_index, end_index):
                row = recommended_recipes.iloc[index]

                with st.container():
                    # Improved image container with perfect centering
                    st.markdown(
                        f"""
                        <div style="
                            height: 200px;
                            width: 100%;
                            margin: 0;
                            padding: 0;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            background-color: #f8f8f8;
                            border-radius: 8px;
                            overflow: hidden;
                        ">
                            <img src="{row['Images'][0]}" style="
                                height: 100%;
                                width: 100%;
                                object-fit: cover;
                                display: block;
                                margin: 0 auto;
                                padding: 0;
                                " onerror="this.src='{DEFAULT_IMAGE}';this.onerror=null;
                            ">
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    # Recipe name with line clamping (max 1 line)
                    st.markdown(
                        f"""
                        <div style="
                            font-size: 1.2rem;
                            font-weight: bold;
                            margin: 8px 0;
                            display: -webkit-box;
                            -webkit-line-clamp: 1;
                            -webkit-box-orient: vertical;
                            overflow: hidden;
                            text-overflow: ellipsis;
                        ">
                            {row['name']}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    # Create columns for rating and button
                    col1, col2 = st.columns([2, 3])  # Adjust ratio as needed
                    
                    with col1:
                        st.write(f"⭐ {row['avg_rating']:.2f} | {row['num_reviews']} reviews")
                    
                    with col2:
                        st.button(
                            "View Details", 
                            key=f"view_recipe{row['recipe_id']}", 
                            on_click=view_recipe_callback, 
                            args=(row["recipe_id"], True),
                            # Optional: make button more compact
                            use_container_width=True
                        )

def app():   
    # Check for personalized recommendations
    user_id = st.session_state.user_data.get('user_id')
    recommended_recipes = None

    if "show_description" not in st.session_state:
        st.session_state.show_description = False
    if "selected_recipe" not in st.session_state:
        st.session_state.selected_recipe = None
    
    # Initialize session state if not set
    if "rec_choice" not in st.session_state:
        st.session_state.rec_choice = None
        
    # Function to handle selection without rerun
    def handle_selection(choice):
        st.session_state.rec_choice = choice
        st.rerun()
    # function to handle return to options 
    def handle_options_btn():
        st.session_state.rec_choice = None

    # Only show cards if no choice has been made yet
    if st.session_state.rec_choice is None:
        # Hero Section
        st.markdown(
            f"""
            <style>
            .hero {{
                background-image: url('https://images.unsplash.com/photo-1504674900247-0877df9cc836?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80');
                background-size: cover;
                background-position: center;
                height: 300px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                text-align: center;
                border-radius: 15px;
                margin-bottom: 2rem;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }}
            .hero h1 {{
                font-size: 3rem;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            }}
            .hero p {{
                font-size: 1.2rem;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
            }}
            </style>
            <div class="hero">
                <div>
                    <h1>Discover Your Next Meal</h1>
                    <p>Personalized recipes tailored just for you, {st.session_state.user_data.get("name", "")}!</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <style>
            .underline-animation {
                display: block;
                position: relative;
                color: #2e8b57;
                text-align: center;
                width: 100%;
                margin: 0 auto;
            }
            .underline-animation:after {
                content: '';
                position: absolute;
                width: 100%;
                transform: scaleX(0);
                height: 3px;
                bottom: 0;
                left: 0;
                background-color: #ff6b6b;
                transform-origin: bottom right;
                transition: transform 0.25s ease-out;
            }
            .underline-animation:hover:after {
                transform: scaleX(1);
                transform-origin: bottom left;
            }
            .title-container {
                font-style: italic;
                text-align: center;
                width: 100%;
                margin-bottom: 2rem;
            }
            </style>
            <div class="title-container">
                <h2 class="underline-animation" style="color: #2e8b57; display: inline-block;">
                    Choose Your Recommendation Type
                </h2>
            </div>
            """,
            unsafe_allow_html=True
        )
        #st.header(f":green[Welcome {st.session_state.user_data.get("name", "")}, _Choose Your Recommendation Type_]")
        # Create a grid for the option cards
        option_grid = grid(3, gap="medium")

        with option_grid.container():
            # Personalized For You Card
            card(
                title="✨ User-Based",
                text="Personalized recommendations based on your taste",
                image="https://images.unsplash.com/photo-1505576399279-565b52d4ac71?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
                on_click=lambda: handle_selection("User-Based"),
                styles={
                    "card": {
                        "width": "100%",
                        "height": "350px",
                        "margin": "0", 
                        "padding": "0",
                        "border-radius": "15px",
                        "box-shadow": "0 4px 8px rgba(0,0,0,0.1)",
                        "transition": "transform 0.3s",
                    },
                    "title": {
                        "font-size": "1.2rem",
                        "color": "#ffffff",
                        "font-weight": "600"
                    },
                    "text": {
                        "font-size": "0.9rem",
                        "color": "#ecf0f1"
                    }
                }
            )

        with option_grid.container():
            # Similar Recipes Card
            card(
                title="🍽️ Item-Based",
                text="Find recipes similar to your favorites",
                image="https://images.unsplash.com/photo-1490645935967-10de6ba17061?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
                on_click=lambda: handle_selection("Item-Based"),
                styles={
                    "card": {
                        "width": "100%",
                        "height": "350px",
                        "margin": "0", 
                        "padding": "0",
                        "border-radius": "15px",
                        "box-shadow": "0 4px 8px rgba(0,0,0,0.1)",
                        "transition": "transform 0.3s",
                    },
                    "title": {
                        "font-size": "1.2rem",
                        "color": "#ffffff",
                        "font-weight": "600"
                    },
                    "text": {
                        "font-size": "0.9rem",
                        "color": "#ecf0f1"
                    }
                }
            )

        with option_grid.container():
            # Popular Recipes Card
            card(
                title="🔥 Popular Choices",
                text="Discover trending recipes among all users.",
                image="https://images.unsplash.com/photo-1546069901-ba9599a7e63c?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
                on_click=lambda: handle_selection("Popular"),
                styles={
                    "card": {
                        "width": "100%",
                        "height": "350px",
                        "margin": "0", 
                        "padding": "0",
                        "border-radius": "15px",
                        "box-shadow": "0 4px 8px rgba(0,0,0,0.1)",
                        "transition": "transform 0.3s",
                    },
                    "title": {
                        "font-size": "1.2rem",
                        "color": "#ffffff",
                        "font-weight": "600"
                    },
                    "text": {
                        "font-size": "0.9rem",
                        "color": "#ecf0f1"
                    }
                }
            )
        
        add_vertical_space(3) # some space
        # Testimonials Section
        st.markdown("""
        <style>
        @keyframes float {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-5px); }
            100% { transform: translateY(0px); }
        }
        
        .testimonial-card {
            background: white;
            padding: 1.5rem;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(46, 139, 87, 0.1);
            height: 220px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            border-left: 4px solid #3aafa9;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .testimonial-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 20px rgba(46, 139, 87, 0.15);
        }
        
        .testimonial-card:before {
            content: '"';
            position: absolute;
            top: 10px;
            left: 10px;
            font-size: 4rem;
            color: rgba(58, 175, 169, 0.1);
            font-family: serif;
        }
        
        .testimonial-avatar {
            font-size: 2rem;
            margin-bottom: 1rem;
            animation: float 3s ease-in-out infinite;
        }
        
        .testimonial-text {
            font-style: italic;
            color: #555;
            margin-bottom: 1rem;
            position: relative;
            z-index: 1;
        }
        
        .testimonial-name {
            font-weight: bold;
            color: #2e8b57;
            margin-top: auto;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown("## 🗣️ What Users Say")
        testimonials = [
            {"name": "Alex", "text": "These recommendations saved my cooking routine! Never knew I could make such delicious meals with what I had.", "avatar": "👨‍🍳"},
            {"name": "Priya", "text": "Found my new favorite dish in minutes. The AI understands my taste better than I do!", "avatar": "👩‍🔬"},
            {"name": "Jordan", "text": "The personalized suggestions are spot-on. My family thinks I've become a gourmet chef overnight.", "avatar": "🧑‍🎤"},
            {"name": "Taylor", "text": "As a busy student, this has been a game-changer. Quick, tasty recipes every time.", "avatar": "👩‍🎓"},
        ]
        
        cols = st.columns(len(testimonials))
        for idx, testimonial in enumerate(testimonials):
            with cols[idx]:
                st.markdown(
                    f"""
                    <div class="testimonial-card">
                        <div class="testimonial-avatar">{testimonial['avatar']}</div>
                        <p class="testimonial-text">"{testimonial['text']}"</p>
                        <p class="testimonial-name">— {testimonial['name']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )


    has_user_based = (
        "user_pred_df" in st.session_state 
        and not st.session_state.user_pred_df.empty
        and user_id in st.session_state.user_pred_df['user_id'].values
    )
    has_item_based = (
        "item_pred_df" in st.session_state 
        and not st.session_state.item_pred_df.empty
        and user_id in st.session_state.item_pred_df['user_id'].values
    )
    # Display recommendations based on selection
    if st.session_state.rec_choice:
        # If User-Based or Item-Based is selected but no recommendations exist, show a warning
        if st.session_state.rec_choice == "User-Based" and not has_user_based:
            st.warning("⚠️ You have not rated enough recipes to receive personalized recommendations.")
            return
        if st.session_state.rec_choice == "Item_Based" and not has_item_based:
            st.warning("⚠️ No similar recipes available. Try rating some recipes first!")
            return
        
        if has_user_based:
            header_text = "✨ Your Personalized Recommendations"
            subheader_text = "Recipes we think you'll love based on your preferences!"
        elif has_item_based:
            header_text = "🔍 Recipes Similar to Your Favorites"
            subheader_text = "Discover recipes similar to the ones you've liked!"
        else:
            user_name = st.session_state.user_data.get('name', '')
            header_text = f"👋 {user_name} Welcome! Check Out Popular Recipes"
            subheader_text = "Not sure what to cook? Here are some of the most-loved recipes!"

        recommended_recipes = get_recipes(personalized=st.session_state.rec_choice)

        # UI rendering
        # Check if a recipe description should be shown    
        if st.session_state.show_description and st.session_state.selected_recipe:
            with st.spinner("Loading selected recipe details..."):
                recipe = recommended_recipes[recommended_recipes['recipe_id']==st.session_state.selected_recipe].iloc[0]
                header_col1, header_col2 = st.columns([3,1])
                with header_col1:
                    st.subheader(f":green[{recipe['name']}]", divider='green')
                with header_col2:
                    st.button("Back to Recommended Recipes",key=f"home_{recipe['recipe_id']}", on_click=view_recipe_callback, args=(None, False))
                show_recipe_description(recipe)
        else:
            header_col1,header_col2 = st.columns([3,1])
            with header_col1:
                st.header(f":blue[{header_text}]")
            with header_col2:
                # Add a back button to show cards again
                st.button("← Back to Recommendation Options", on_click=handle_options_btn)

            st.subheader(f":green[{subheader_text}]")
            with st.spinner("Loading recommended recipes..."):            
                show_recipes(recommended_recipes)

    