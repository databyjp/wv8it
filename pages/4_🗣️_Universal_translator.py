import streamlit as st
import utils
from config import (
    wiki_name,
    chunks_index_name,
)
from weaviate.classes.query import Filter

with utils.get_weaviate_client() as client:

    intro_tab, demo_tab, explanation_tab = st.tabs(["Introduction", "Demo", "What does it mean for me?"])

    with intro_tab:
        st.header("(Almost) Universal translation! 🗣️🗣️🗣️")

        st.image("./assets/trek_translator.jpg", width=500)

    with demo_tab:
        blank_selection = "Select a language"
        lang_map = {
            "English": "simple",
            "French": "fr",
            "Korean": "ko",
            "Dutch": "nl",
        }

        lang_selection = st.selectbox(
            "Select a language",
            [blank_selection, "English", "French", "Korean", "Dutch", "Any"],
        )

        questions = [
            "Formula one cars",
            "Motorsport vehicle",
            "Dog",
            "Chien",
            "Ruimtereis",
            "코리아 그랑프리",
        ]
        question_caption = "Find entries about..."
        user_query = utils.type_or_select_question(questions=questions, question_caption=question_caption)

        if lang_selection != blank_selection:
            wiki_coll = client.collections.get(wiki_name)
            if lang_selection != "Any":
                filter = Filter.by_property("lang").equal(lang_map[lang_selection])
            else:
                filter = None

            if user_query:
                response = wiki_coll.query.near_text(
                    query=user_query,
                    target_vector=chunks_index_name,
                    filters=filter,
                    limit=10,
                )

                for result in response.objects:
                    chunk_no = result.properties["chunk_no"]
                    with st.expander(
                        result.properties["title"] + f" (chunk {chunk_no})"
                    ):
                        st.write(result.properties["text"])

    with explanation_tab:
        points = [
            "- ##### Remove any needs to translate data at input or output",
            "- ##### Meet your users where they are",
        ]

        utils.explain_meaning(points=points)
