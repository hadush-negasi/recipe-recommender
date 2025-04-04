import streamlit as st
import numpy as np
import requests
from recipe_display import show_recipe_description, view_recipe_callback

# check if all selected tags are present in the recipe
def all_tags_present(item_tags, selected):
    return all(string in item_tags for string in selected)


# check if all ingredients are available in specific recipe
def check_ingredients_df(row, selected):
    ing_matched = row
    # Join all ingredients into a single lowercase string
    ing_str = ' '.join(str(ing).lower() for ing in ing_matched)
    #check each item in ing_selected
    for item in selected:
        if item not in ing_str:
            return False
    # If we've made it through all items without returning False, return True
    return True


def truncate_text(text, word_limit=20):
    """Truncates text to a specific number of words and adds '...' if longer."""
    words = text.split()  # Split text into words
    if len(words) > word_limit:
        return " ".join(words[:word_limit]) + "..."  # Keep only the first `word_limit` words
    return text  # Return full text if it's short enough


def is_valid_image(url):
    """Check if the image URL is valid by sending a HEAD request."""
    try:
        response = requests.head(url, timeout=3)  # Quick check
        return response.status_code == 200  # Return True if valid
    except requests.RequestException:
        return False  # Return False if the request fails

def clear_result_callback():
    #clear previous search results
    view_recipe_callback(None, False) # clear the selected recipe details
    st.session_state.search_results = None
    st.session_state.matching_recipes_page = 1

def handle_select_recipe(recipe_id):
    st.session_state.selected_recipe = recipe_id
    st.session_state.show_description = True

# Filter out recipes to find a match base on the inputs tags, ingredients, max minutes, number of steps to cook
def filter_recipes(tags_selected, ing_selected, max_minutes, max_steps):
    recipes_df = st.session_state.recipes_df
    ing_selected = ing_selected.split(',')
    recipe_rec = recipes_df[['recipe_id', 'tags', 'ingredients', 'minutes', 'n_steps']].copy()
    #Filter by tags
    if tags_selected:
        recipe_rec['tag_match'] = recipe_rec['tags'].apply(all_tags_present, selected=tags_selected)
        recipe_rec = recipe_rec[recipe_rec['tag_match'] == True]
    #Filter by ingredients
    if ing_selected:
        recipe_rec['ing_match'] = recipe_rec['ingredients'].apply(check_ingredients_df, selected=ing_selected)
        recipe_rec = recipe_rec[recipe_rec['ing_match'] == True]
    # Filter by maximum cooking time
    if max_minutes is not None:
        recipe_rec = recipe_rec[recipe_rec['minutes'] <= max_minutes]
    # Filter by maximum number of steps
    if max_steps is not None:
        recipe_rec = recipe_rec[recipe_rec['n_steps'] <= max_steps]
    
    recipe_id = recipe_rec['recipe_id'].values
    recipe_steps_rec= recipes_df[recipes_df['recipe_id'].isin(recipe_id)][['recipe_id', 'name', 'description', 'minutes', 'n_steps', 'Images']]
    return recipe_steps_rec

# Improved Pagination function for recipes display recipes in pages with expander function
def paginate_recipes(recipes, page_size=5, page_state_key="current_page"):
    total_recipes = len(recipes)
    total_pages = (total_recipes // page_size) + (1 if total_recipes % page_size > 0 else 0)
    # Initialize session state for the current page if it doesn't exist
    if page_state_key not in st.session_state:
        st.session_state[page_state_key] = 1
    #st.write(f"Total Recipes: {total_recipes}, Total Pages: {total_pages}, Current Page: {st.session_state[page_state_key]}")

    # Create Previous/Next buttons for pagination with callbacks
    def previous_page():
        if st.session_state[page_state_key] > 1:
            st.session_state[page_state_key] -= 1
    def next_page():
        if st.session_state[page_state_key] < total_pages:
            st.session_state[page_state_key] += 1
    # Create Previous/Next buttons for pagination
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.session_state[page_state_key] > 1:
            st.button("Previous", key=f"prev_{page_state_key}", on_click=previous_page)

    with col3:
        if st.session_state[page_state_key] < total_pages:
            st.button("Next", key=f"next_{page_state_key}", on_click=next_page)
    #st.write(f"Total Recipes: {total_recipes}, Total Pages: {total_pages}, Current Page: {st.session_state[page_state_key]}")

    # Get the recipes to display on the current page
    start_idx = (st.session_state[page_state_key] - 1) * page_size
    end_idx = start_idx + page_size
    paginated_recipes = recipes.iloc[start_idx:end_idx]
    DEFAULT_IMAGE = "https://via.placeholder.com/200x300?text=No+Image"

    # Display the paginated recipes using expanders and select buttons
    for _, recipe in paginated_recipes.iterrows():
        with st.expander(f"Recipe: {recipe['name']} (Cooking Time: {recipe['minutes']} min)"):
            # Create two columns: one for the image, one for the description
            col1, col2 = st.columns([1, 2])  # Adjust width ratio as needed
            recipe_id = recipe['recipe_id']
            # Display Recipe Image in the First Column
            with col1:
                with st.container():
                    # Image container with identical styling to your reference
                    st.markdown(
                        f"""
                        <div style="
                            height: 100px;
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
                            <img src="{recipe['Images'][0]}" 
                                 style="
                                    height: 100%;
                                    width: 100%;
                                    object-fit: cover;
                                    display: block;
                                    margin: 0 auto;
                                    padding: 0;
                                 "
                                 onerror="this.src='{DEFAULT_IMAGE}';this.onerror=null;"
                                 alt="Recipe image">
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    st.write(f"Number of Steps: {recipe['n_steps']}")

            # Display Recipe Description in the Second Column
            with col2:
                if recipe["description"]:
                    st.markdown(
                        f"""
                        <div style="
                            margin-bottom: 8px;
                            display: -webkit-box;
                            -webkit-line-clamp: 3;
                            -webkit-box-orient: vertical;
                            overflow: hidden;
                            text-overflow: ellipsis;
                        ">
                            {recipe['description']}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                # Button to select the recipe
                st.button(f"Select {recipe['name']}", key=f"select_{recipe_id}", on_click=handle_select_recipe, args=(recipe['recipe_id'],), use_container_width=True)
                    
            # Conditionally render the markdown after the button is clicked
            if st.session_state.show_description and st.session_state.selected_recipe == recipe['recipe_id']:
                st.markdown(f"<a href='#selected_recipe'>go to recipe</a>", unsafe_allow_html=True)
    # Display current page information
    st.write(f"Page {st.session_state[page_state_key]} of {total_pages}")


def app():
    #place the header on the left side of page
    st.header(":blue[_What’s Cooking? Find Recipes Instantly!_] 🍽️")

    if "show_description" not in st.session_state:
        st.session_state.show_description = False
    if "selected_recipe" not in st.session_state:
        st.session_state.selected_recipe = None

    # Set session state for recipe viewing mode
    if "search_results" not in st.session_state:
        st.session_state.search_results = None # stores the filtered recipes  
    
    # Initialize session state for the current page if it doesn't exist
    if "matching_recipes_page" not in st.session_state:
        st.session_state.matching_recipes_page = 1
    
    tag_options = ['60-minutes-or-less', '30-minutes-or-less', '15-minutes-or-less', 'easy', 'meat', 'poultry', 'vegetables', 
               'fruit', 'pasta-rice-and-grains', 'inexpensive', 'dietary', 'healthy', 'low-carb', 'low-sodium', 'low-saturated-fat', 'low-calorie', 
               'low-cholesterol', 'low-fat', 'breakfast', 'beginner-cook']

    # Create a centered form with limited width
    col1, col2 = st.columns([1, 2])  # Middle column is wider
    with col1:
        # form to collect recipe tags, ingredients, number of cooking steps, total minute
        with st.form(key='search_form'):
            tags_selected = st.multiselect("Please select any tags for a meal you are interested in.", tag_options)

            ing_selected = st.text_input('Please enter any ingredients you have on hand separated by commas.',
                                         help='Use lowercase and plural form when appropriate', autocomplete='off')
            # Input for the maximum number of minutes
            max_minutes = st.number_input('Select Maximum Cooking Time (minutes)', 
                                              min_value=1, 
                                              max_value=120,  # Set a max value based on your dataset
                                              value=None)  # Default value

            # Input for the maximum number of steps
            max_steps = st.number_input('Select Maximum Number of Steps', 
                                           min_value=1, 
                                           max_value=24,  # Set a max value based on your dataset
                                           value=None)  # Default value

            submit = st.form_submit_button('Search for matching Recipes')

        # after submission
        if submit:
            with st.spinner("Searching for Matching Recipes..."):
                # run recipe filter and store result in session state
                # clear previous search result
                st.session_state.search_results = None
                st.session_state.matching_recipes_page = 1
                st.session_state.show_description = False
                st.session_state.search_results = filter_recipes(tags_selected, ing_selected, max_minutes, max_steps)
    with col2:
        # Display search results 
        if st.session_state.search_results is not None:
            with st.container(border=True):
                if not st.session_state.search_results.empty:
                    header_col1,header_col2 = st.columns([3,1])
                    with header_col1:
                        st.subheader(':green[Matching Recipes]', divider='green')
                    with header_col2:
                        st.button("Clear Search Results", on_click=clear_result_callback)

                    # Reset the page number to first page
                    paginate_recipes(st.session_state.search_results, page_size=5, page_state_key='matching_recipes_page')   
                else:
                    st.write("Couldn't find matching recipes.")

    # Display selected recipe details if a recipe is selected
    if st.session_state.show_description and st.session_state.selected_recipe is not None:
        with st.container(border=True):
            # Use st.status for a persistent loading indicator
            with st.spinner("Loading selected recipe details..."):
                recipe = st.session_state.recipes_df[st.session_state.recipes_df['recipe_id'] == st.session_state.selected_recipe].iloc[0]
                st.subheader(f":green[{recipe['name']}]", divider='green', anchor='selected_recipe')
                # Display selected recipe
                show_recipe_description(recipe)
              
            