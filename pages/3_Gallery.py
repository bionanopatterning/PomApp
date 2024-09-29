import streamlit as st
import json
import pandas as pd
import os
from PIL import Image
import numpy as np

st.set_page_config(
    page_title="Gallery",
    layout='wide'
)

with open("project_configuration.json", 'r') as f:
    project_configuration = json.load(f)


def get_image(tomo, image):
    image_dir = image.split("_")[0]
    img_path = os.path.join("images", image_dir, f"{tomo}_{image}.png")
    if os.path.exists(img_path):
        return Image.open(img_path)
    else:
        return Image.fromarray(np.zeros((128, 128)), mode='L')


@st.cache_data
def load_data():
    cache_df = pd.read_excel(os.path.join(project_configuration["root"], "summary.xlsx"), index_col=0)
    cache_df = cache_df.dropna(axis=0)
    return cache_df


df = load_data()

# Initialize session state variables
if 'page_num' not in st.session_state:
    st.session_state.page_num = 0

if 'search_query' not in st.session_state:
    st.session_state.search_query = ""

if 'display_option' not in st.session_state:
    st.session_state.display_option = "Macromolecules"


def reset_page_number():
    st.session_state.page_num = 0


# Title and info text
st.title("Tomogram Gallery")
st.write(
    "Browse through the collection of tomograms. Use the search bar to filter tomograms by name. You can choose to view either **Macromolecules** or **Top3 ontologies** 3D renders.")

# Search bar and display option
col1, col2 = st.columns([3, 1])

with col1:
    search_query = st.text_input(
        "Search tomograms",
        value=st.session_state.search_query,
        key='search_query',
        on_change=reset_page_number
    )

with col2:
    options = ["Macromolecules", "Top ontologies"]
    index = options.index(st.session_state.display_option) if 'display_option' in st.session_state else 0
    display_option = st.selectbox(
        "Display option",
        options,
        index=index,
        key='display_option',
        on_change=reset_page_number
    )

# Filter tomograms based on search query
tomogram_names = df.index.tolist()

if st.session_state.search_query:
    tomogram_names = [name for name in tomogram_names if st.session_state.search_query.lower() in name.lower()]

if not tomogram_names:
    st.write("No tomograms found matching the search query.")
else:
    # Pagination variables
    tomograms_per_page = 16
    total_pages = (len(tomogram_names) - 1) // tomograms_per_page + 1

    # Ensure page number is within valid range
    if st.session_state.page_num > total_pages - 1:
        st.session_state.page_num = total_pages - 1
    if st.session_state.page_num < 0:
        st.session_state.page_num = 0

    # Get tomograms to display on the current page
    start_idx = st.session_state.page_num * tomograms_per_page
    end_idx = start_idx + tomograms_per_page
    tomograms_to_display = tomogram_names[start_idx:end_idx]

    # Display images in a 4x4 grid
    n_cols = 4
    for idx in range(0, len(tomograms_to_display), n_cols):
        tomos_in_row = tomograms_to_display[idx:idx + n_cols]
        cols = st.columns(n_cols)
        for col, tomo_name in zip(cols, tomos_in_row):
            with col:
                # Make the tomogram name clickable
                st.markdown(
                    f"<div style='text-align: center; font-size:14px; margin-bottom:5px;'>"
                    f"<a href='/Browse_tomograms?tomo_id={tomo_name}' style='text-decoration: none; color: inherit;'>{tomo_name}</a>"
                    f"</div>",
                    unsafe_allow_html=True
                )

                if st.session_state.display_option == "Macromolecules":
                    image = get_image(tomo_name, "Macromolecules")
                else:
                    image = get_image(tomo_name, "Top3")

                # Display the image
                st.image(image, use_column_width=True)


    # Pagination buttons
    def prev_page():
        if st.session_state.page_num > 0:
            st.session_state.page_num -= 1


    def next_page():
        if st.session_state.page_num < total_pages - 1:
            st.session_state.page_num += 1


    # Adjust the column widths for better alignment
    col_prev, col_page_num, col_next = st.columns([3, 14, 1])

    with col_prev:
        if st.session_state.page_num > 0:
            st.button("Previous", on_click=prev_page)
        else:
            st.markdown("")  # Placeholder to keep alignment

    with col_page_num:
        st.markdown(f"<div style='text-align: center;'>Page {st.session_state.page_num + 1} of {total_pages}</div>",
                    unsafe_allow_html=True)

    with col_next:
        if st.session_state.page_num < total_pages - 1:
            st.button("Next", on_click=next_page)
        else:
            st.markdown("")  # Placeholder to keep alignment
