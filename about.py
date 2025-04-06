import streamlit as st
from streamlit_extras.card import card

def app():
    try:
        # ---- Hero Section ----
        st.markdown(
            """
            <style>
            .hero {
                background: linear-gradient(135deg, #2e8b57 0%, #3aafa9 100%);
                padding: 3rem;
                border-radius: 15px;
                color: white;
                text-align: center;
                margin-bottom: 2rem;
            }
            .hero h1 {
                font-size: 2.5rem;
                margin-bottom: 0.5rem;
            }
            </style>
            <div class="hero">
                <h1>About Recipe Recommender</h1>
                <p>Smart recipes for students and busy professionals</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # ---- Key Features Grid ----
        st.subheader("✨ How It Works Now")
        cols = st.columns(3)
        with cols[0]:
            card(
                title="Personalized for You",
                text="User-based collaborative filtering learns from your ratings to suggest recipes you'll love.",
                image="https://images.unsplash.com/photo-1606787366850-de6330128bfc?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=80",
                styles={
                    "card": { 
                        "width": "100%",
                        "background-color": "#f8f9fa",
                        "margin": "0", 
                        "padding": "0",
                        }
                }
            )
        with cols[1]:
            card(
                title="Discover New Favorites",
                text="Content-based search recommends similar recipes for new users or when exploring ingredients.",
                image="https://images.unsplash.com/photo-1547592180-85f173990554?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=80",
                styles={
                    "card": { 
                        "width": "100%",
                        "background-color": "#f8f9fa",
                        "margin": "0", 
                        "padding": "0",
                        }
                }
            )
        with cols[2]:
            card(
                title="Trending Recipes",
                text="See what's popular across our community with real-time trending dishes.",
                image="https://images.unsplash.com/photo-1490645935967-10de6ba17061?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=80",
                styles={
                    "card": { 
                        "width": "100%",
                        "background-color": "#f8f9fa",
                        "margin": "0", 
                        "padding": "0",
                        }
                }
            )

        # ---- Detailed Explanation ----
        with st.expander("📚 Learn About Our Technology"):
            st.markdown("""
            **Our Hybrid Recommendation System**  
            🔹 **User-Based Collaborative Filtering**:  
            - Suggests recipes based on preferences from users like you  
            - Improves over time as you rate recipes  

            🔹 **Content-Based Search**:  
            - Finds recipes with similar ingredients/tags for new users  
            - Great for using up pantry items  

            🔹 **Popular Recipes**:  
            - Real-time trending dishes loved by the community  
            """)

        # ---- Testimonials ----
        st.subheader("🍳 What Users Say")
        testimonial_cols = st.columns(2)
        with testimonial_cols[0]:
            st.markdown("""
            <div style="
                background: #f8f9fa;
                padding: 1.5rem;
                border-radius: 10px;
                border-left: 4px solid #2e8b57;
            ">
            <i>"The personalized recommendations saved me so much time! 
            I discovered 5 new favorite recipes in my first week."</i>
            <br><br>
            <b>— Sarah, College Student</b>
            </div>
            """, unsafe_allow_html=True)

        with testimonial_cols[1]:
            st.markdown("""
            <div style="
                background: #f8f9fa;
                padding: 1.5rem;
                border-radius: 10px;
                border-left: 4px solid #3aafa9;
            ">
            <i>"As someone who hates meal planning, the trending recipes section 
            is a game-changer. Always find something delicious!"</i>
            <br><br>
            <b>— Michael, Busy Professional</b>
            </div>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.error("Oops! Something went wrong.")
