import streamlit as st

def getRecommendations(user_id, filter_type='User-Based', top_n=10):
    user_pred = st.session_state.user_pred_df
    item_pred = st.session_state.item_pred_df
    reviews_df = st.session_state.reviews_df
    
    # Select the appropriate prediction DataFrame
    if filter_type == "User-Based":
        pred_df = user_pred
    elif filter_type == "Item-Based":
        pred_df = item_pred
    else:
        raise ValueError("Invalid method! Choose either 'user' or 'item'.")
    # find all the recipes rated by the given user 
    recipes_rated = list(reviews_df['recipe_id'].loc[reviews_df['user_id'] == user_id])
    # select the row of predicted rating by the given user from the user_prediction dataframe
    predicted_rating = pred_df.loc[pred_df['user_id'] == user_id].copy()
    # drop the rated recipes columns and store the predicted rating of unrated recipes 
    predicted_rating.drop(pred_df[recipes_rated], axis = 1, inplace = True)
    # sort the predicted rating of recipes by the user column wise
    unrated_recipes = predicted_rating.iloc[:,1:].sort_values(by = predicted_rating.index[0], axis = 1, ascending = False)
    # Selects only the top N columns (recipes) with the highest predicted ratings.
    # Converts the DataFrame into a list of dictionaries, where: Keys are recipe IDs. Values are predicted ratings.
    dict_top_n = unrated_recipes.iloc[:, :top_n].to_dict(orient = 'records') 
    return dict_top_n[0]

def display_recipes(recommendations, filter_type, user_id):
    recipes_df = st.session_state.recipes_df
    recommended_recipes = []
    for recipe_id in recommendations.keys():
        recipe_details = recipes_df.loc[recipes_df["recipe_id"] == recipe_id, ["name", "minutes", "description"]]
        if not recipe_details.empty:
            name = recipe_details["name"].values[0]
            minutes = recipe_details["minutes"].values[0]
            description = recipe_details["description"].values[0]
            recommended_recipes.append((name, minutes, description))
    # Select the appropriate prediction DataFrame
    if filter_type == "User-Based":
        st.write(f"Using User-Based Collaborative Filtering for User ID: {user_id}")
    elif filter_type == "Item-Based":
        st.write(f"Using Item-Based Collaborative Filtering for User ID: {user_id}")
    # Display recommendations
    for idx, (name, minutes, description) in enumerate(recommended_recipes, start=1):
        st.subheader(f"Top {idx}: {name}")
        st.write(f"⏱ **Time Required:** {minutes} minutes")
        st.write(f"📖 **Description:** {description}")
        st.markdown("---")



def app():
    try:
        st.sidebar.header("Recipe Recommendation System")
        # Get the maximum user_id dynamically
        max_user_id = st.session_state.user_pred_df["user_id"].max()

        # Create a form in the sidebar
        with st.sidebar.form(key="recommendation_form"):
            userid = st.number_input("User ID", min_value=0, max_value=max_user_id, value=5, step=1)
            filter_type = st.selectbox("Select Recommendation Type", ["User-Based", "Item-Based"])
            n_items = st.number_input("Number of Recommendations", min_value=1, max_value=20, value=5, step=1)

            # Submit button (only triggers when clicked)
            search_button = st.form_submit_button("Search")

        # Main Page Output
        st.title("Recommended Recipes")
        if search_button and userid:
            recommendations = getRecommendations(userid, filter_type, n_items)
            display_recipes(recommendations, filter_type, userid)
        else:
            st.write("Enter a User ID and click Search to get recommendations.")
    except Exception as e:
        st.error("Oops! Something went wrong.")
