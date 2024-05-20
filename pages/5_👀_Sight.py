import streamlit as st
import utils
from config import (
    multimodal_name,
    chunks_index_name,
)
from weaviate.classes.query import Filter

with utils.get_weaviate_client() as client:
    st.header("Vision-based search! 👀")

    # Get the collection
    movies = client.collections.get(multimodal_name)

    demo_tab, explanation_tab = st.tabs(["Demo", "What does it mean for me?"])

    with demo_tab:
        img_tab, text_tab = st.tabs(["Image search", "Text search"])

        with img_tab:
            input_col, preview_col = st.columns(2)
            with input_col:
                user_image = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])
            with preview_col:
                if user_image:
                    st.image(user_image, caption="Your image", width=200)

            # Show results in 5 columns
            col1, col2, col3, col4, col5 = st.columns(5)

            if user_image:
                query_b64 = utils.to_base64(user_image.getvalue())

                response = movies.query.near_image(
                    near_image=query_b64,
                    limit=5,
                    return_properties=["title", "release_date", "tmdb_id", "poster"]  # To include the poster property in the response (`blob` properties are not returned by default)
                )

                for i, o in enumerate(response.objects):
                    img = utils.base64_to_image(o.properties["poster"])
                    with locals()[f"col{i+1}"]:
                        st.image(img, caption=o.properties["title"], use_column_width=True)


        with text_tab:
            user_query = st.text_input("Find images like...")

            # Show results in 5 columns
            col1, col2, col3, col4, col5 = st.columns(5)

            if user_query:
                response = movies.query.near_text(
                    query=user_query,
                    limit=5,
                    return_properties=["title", "release_date", "tmdb_id", "poster"]  # To include the poster property in the response (`blob` properties are not returned by default)
                )

                for i, o in enumerate(response.objects):
                    img = utils.base64_to_image(o.properties["poster"])
                    with locals()[f"col{i+1}"]:
                        st.image(img, caption=o.properties["title"], use_column_width=True)


    with explanation_tab:
        points = [
            "- ##### Multi-modal search at your fingertips",
            "- ##### Search images and text with images or text",
        ]

        utils.explain_meaning(points=points)
