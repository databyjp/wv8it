import streamlit as st
import utils
from config import (
    wiki_name,
    etienne_collection_name,
    knowledge_base_name,
    chunks_index_name,
)

with utils.get_weaviate_client() as client:

    intro_tab, demo_tab = st.tabs(["Introduction", "Demo"])

    with intro_tab:
        st.header("Find what you need! 🔍")

        st.image("./assets/messy_room.jpg", width=500)

    with demo_tab:
        questions = [
            "Formula one cars",
            "Motorsport vehicle",
            "Space travel",
            "Intergalactic voyage",
        ]
        question_caption = "Find entries about..."
        user_question = utils.type_or_select_question(questions=questions, question_caption=question_caption)

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
