import streamlit as st
import utils
from config import wiki_name, wiki_index_name
from weaviate.classes.query import Filter

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

        lang_selection = st.selectbox("Select a language", [blank_selection, "English", "French", "Korean", "Dutch"])
        user_query = st.text_input("Find information about...")
        top_n = st.slider("How many results?", 1, 20, 10)
        if lang_selection != blank_selection:
            wiki_coll = client.collections.get(wiki_name)
            response = wiki_coll.query.near_text(
                query=user_query,
                target_vector=wiki_index_name,
                filters=Filter.by_property("lang").equal(lang_map[lang_selection]),
                limit=top_n
            )

            print(response)
            for result in response.objects:
                with st.expander(result.properties["title"] + " " + str(result.properties["chunk_no"])):
                    st.write(result.properties["text"])
