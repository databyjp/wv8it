import streamlit as st
import utils
from config import wiki_name, chunks_index_name
from weaviate.classes.query import Filter

with utils.get_weaviate_client() as client:
    st.header("Speak all the languages, fluently! 🗣️🗣️🗣️")

    demo_tab, explanation_tab = st.tabs(["Demo", "What does it mean for me?"])

    with demo_tab:
        search_responses = utils.search_comparison(
            client=client, collection_name=wiki_name, user_query="sports"
        )

        for index, response in search_responses.items():
            st.write(f"Index: {index}")
            st.write(response[1])

    with explanation_tab:
        st.subheader("Multilingual support!")
        st.markdown(
            """
            - ##### No need to translate data at input or output
            - ##### Meet your users where they are
            - ##### Easy data aggregation across languages
            """
        )
