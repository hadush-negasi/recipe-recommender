import streamlit as st
import numpy as np

def view_recipe_callback(recipe_id, show_description):
    """
    Callback function to update session state when "View Details" is clicked.
    """
    st.session_state.selected_recipe = recipe_id
    st.session_state.show_description = show_description

# Dispalay selected recipe
def show_recipe_description(recipe):
    # Access the dataframe from the session
    reviews_df = st.session_state.reviews_df
    #start_time = time.time()
    col1, col2, col3 = st.columns([2,3,1])
    with col1:
        st.subheader(':green[Images]', divider='green')
        st.write("Scroll to see all images")
        DEFAULT_IMAGE = "https://via.placeholder.com/200x300?text=No+Image"
        image_urls = recipe['Images']
        # Convert NumPy array to a list (if needed)
        if isinstance(image_urls, np.ndarray):  
            image_urls = image_urls.tolist()
        # Custom CSS for a horizontal scrollable gallery
        st.markdown(
            """
            <style>
            .scrollable-gallery {
                display: flex;
                overflow-x: auto;
                white-space: nowrap;
                padding: 10px;
                gap: 10px;
                scrollbar-width: thin;
                scrollbar-color: #ccc #f4f4f4;
            }
            .scrollable-gallery img {
                height: 150px; /* Adjust height */
                border-radius: 10px;
                object-fit: cover;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        # Create the gallery HTML correctly
        image_html = """
        <div class="scrollable-gallery">
        """ + "\n".join([
            f"""<img src="{img_url}" 
                 style="height:300px;"
                 onerror="this.src='{DEFAULT_IMAGE}';this.onerror=null;"
                 loading="lazy">"""
            for img_url in image_urls[:5]
        ]) + """
        </div>
        """
        # Display the horizontal scrollable image gallery
        st.markdown(image_html, unsafe_allow_html=True)
        with st.container(height=150):
            if recipe['description']:
                st.write(f"Description: {recipe['description']}")
        st.write(f"Cooking Time: {recipe['minutes']} minutes")
    with col2:
        with st.container(border=True):
            st.subheader(':green[Directions]', divider='green')
            num = 1
            for step in recipe['steps']:
                st.write(f"Step {num}: {step.capitalize()}")
                num += 1
    with col3:
        with st.container(border=True):
            st.subheader(':green[Ingredients]', divider='green')
            with st.container(height=300):
                for ingredient in recipe['ingredients']:
                    st.write(ingredient.capitalize())
    feedback_col1,feedback_col2 = st.columns([1,1])
    with feedback_col1:
        # Feedback Section
        st.subheader(":green[Your Feedback]", divider='green')

        # Check if the user has already rated this recipe
        user_has_rated = False
        user_id = st.session_state.user_data.get('user_id')
        # Check if the user has rated this recipe
        user_has_rated = not reviews_df[
            (reviews_df['user_id'] == user_id) & 
            (reviews_df['recipe_id'] == recipe['recipe_id'])
        ].empty

        if not user_has_rated:
            # Use a form to collect feedback
            with st.form(key='feedback_form', clear_on_submit=True):
                st.write("How would you rate this recipe?")
                # Collect feedback using st.slider and st.text_input inside the form
                feedback_rating = st.feedback(options="stars")
                # Accept multi-line comments using st.text_area()
                feedback_comment = st.text_area(
                    label="Write your review (optional)",
                    placeholder="Share your thoughts about this recipe...",
                    max_chars=300
                )
                # Submit button for the form
                submit = st.form_submit_button("Submit Feedback")
            if submit:
                if feedback_rating is None:
                    st.error("⚠️ Please select a rating before submitting.")
                else:
                    feedback_rating = feedback_rating + 1
                    #print(user_id)
                    st.write("feedback_rating: ", feedback_rating)
                    st.write("feedback comment: ", feedback_comment)
                    #print("feedback_rating: ", feedback_rating)
                    #print("feedback comment: ", feedback_comment)
                    # Append feedback to reviews_df
                    new_review = {
                        'user_id': user_id,  # Assign the new user_id
                        'recipe_id': recipe['recipe_id'],
                        'rating': feedback_rating,
                    }
                    reviews_df.loc[len(reviews_df)] = new_review
                    #st.write(new_review)
                    #print(reviews_df[reviews_df['user_id']==user_id])
                    # Save the updated reviews_df to the feather file
                    reviews_df.to_feather('Data/reviews_df.feather')
                    # Mark feedback as submitted
                    st.session_state.feedback_submitted = True
                    st.success("Thank you for your feedback! 🎉")
                    st.cache_data.clear() # clear cached data so it shows updated recipes
        else:
            st.info("You've already rated this recipe. Thank you! 🎉")
    #print(f"Time taken show selected recipe: {time.time() - start_time:.2f} seconds")
