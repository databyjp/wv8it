import streamlit as st
import utils
from config import (
    wiki_name,
    etienne_collection_name,
    knowledge_base_name,
    chunks_index_name,
)

with utils.get_weaviate_client() as client:
    st.header("LLMs are amazing, but...")

    # Have the user ask a question, either by selecting a question from a list or by typing one in
    type_own_question = "Or, type your own question"
    questions = [
        "What is the capital of France?",
        "Explain how LLMs work, in a couple of short sentences. In English, then in Dutch, please.",
        "Explain what LLaMa is, and what the latest model is, in a few short sentences.",
        type_own_question,
    ]
    selected_question = st.selectbox(
        "Select a question", questions, index=len(questions) - 1
    )

    if selected_question == type_own_question:
        user_question = st.text_input("Ask a question")
    else:
        user_question = selected_question

    # available_collections = client.collections.list_all(simple=True)
    # available_collections_list = list(available_collections.keys())

    selected_collection = st.selectbox(
        label="Select a collection (for RAG)",
        options=[knowledge_base_name, wiki_name, etienne_collection_name],
        index=0,
    )

    if user_question:
        llm_response = utils.ask_llm(user_question)

        llm_tab, rag_tab = st.columns(2)
        with llm_tab:
            st.subheader("LLM says:")
            st.write(llm_response)

        with rag_tab:
            st.subheader("RAG says:")

            rag_response = utils.ask_rag(
                client=client,
                user_prompt=user_question,
                collection_name=selected_collection,
                target_vector=chunks_index_name,
            )

            st.write(rag_response.generated)

            for o in rag_response.objects:
                with st.expander(o.properties["title"]):
                    st.write(o.properties["text"])
