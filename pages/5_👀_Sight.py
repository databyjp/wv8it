import streamlit as st
import utils
from config import (
    wiki_name,
    chunks_index_name,
)
from weaviate.classes.query import Filter

state_key = "multilingual_counter"

with utils.get_weaviate_client() as client:
    st.header("Speak all the languages, fluently! 🗣️🗣️🗣️")

    demo_tab, explanation_tab = st.tabs(["Demo", "What does it mean for me?"])

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
            [blank_selection, "English", "French", "Korean", "Dutch"],
        )
        user_query = st.text_input("Find information about...")
        # top_n = st.slider("How many results?", 1, 20, 10)
        top_n = 10

        if lang_selection != blank_selection:
            wiki_coll = client.collections.get(wiki_name)
            if user_query:
                try:
                    response = wiki_coll.query.near_text(
                        query=user_query,
                        target_vector=chunks_index_name,
                        filters=Filter.by_property("lang").equal(
                            lang_map[lang_selection]
                        ),
                        limit=top_n,
                    )
                except:
                    response = wiki_coll.query.near_text(
                        query=user_query,
                        target_vector="flat",
                        filters=Filter.by_property("lang").equal(
                            lang_map[lang_selection]
                        ),
                        limit=top_n,
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

        utils.explain_meaning(points=points, state_key=state_key)
