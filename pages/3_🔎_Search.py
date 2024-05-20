import streamlit as st
import utils
from config import (
    wiki_name,
    etienne_collection_name,
    knowledge_base_name,
    chunks_index_name,
)

with utils.get_weaviate_client() as client:
    st.header("Search types, compared 🧐🔍🔎")

    # Have the user ask a question, either by selecting a question from a list or by typing one in
    type_own_question = "Or, type your own question"
    questions = [
        "Historical events",
        "Events in the Antipodes",
        "Formula 1 driver",
        type_own_question,
    ]

    selected_question = st.selectbox(
        "Select a question", questions, index=len(questions) - 1
    )

    if selected_question == type_own_question:
        user_question = st.text_input("Ask a question")
    else:
        user_question = selected_question

    selected_collection = st.selectbox(
        label="Select a collection",
        options=[wiki_name, knowledge_base_name, etienne_collection_name],
        index=0,
    )
    collection = client.collections.get(selected_collection)

    if user_question:
        keyword_tab, vector_tab = st.columns(2)
        with keyword_tab:
            st.subheader("Keyword search:")
            keyword_response = collection.query.bm25(
                query=user_question,
                limit=5,
            )

            for o in keyword_response.objects:
                with st.expander(o.properties["title"]):
                    st.write(o.properties["text"])

        with vector_tab:
            st.subheader("Vector search:")
            vector_response = collection.query.near_text(
                query=user_question,
                limit=5,
                target_vector=chunks_index_name,
            )

            for o in vector_response.objects:
                with st.expander(o.properties["title"]):
                    st.write(o.properties["text"])
