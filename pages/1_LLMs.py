import streamlit as st
import utils
from config import wiki_name

with utils.get_weaviate_client() as client:
    st.subheader("LLMs are amazing!")

    # Have the user ask a question, either by selecting a question from a list or by typing one in
    type_own_question = "Or, type your own question"
    questions = [
        "What is the capital of France?",
        "Who is JP Hwang? Provide a short bio.",
        "Explain what LLaMa is, and what the latest model is, in a few short sentences.",
        type_own_question,
    ]
    selected_question = st.selectbox(
        "Select a question", questions, index=len(questions) - 1
    )

    print(selected_question)
    if selected_question == type_own_question:
        user_question = st.text_input("Ask a question")
    else:
        user_question = selected_question

    available_collections = client.collections.list_all(simple=True)
    available_collections_list = list(available_collections.keys())
    try:
        preselected_collection = available_collections_list.index(wiki_name)
    except ValueError:
        preselected_collection = 0

    if user_question:
        llm_response = utils.ask_llm(user_question)
        rag_response = utils.ask_rag(
            client=client,
            user_prompt=user_question,
            collection_name=wiki_name,
            target_vector="chunk",
        )

        llm_tab, rag_tab = st.tabs(["LLM", "LLM+"])
        with llm_tab:
            st.subheader("LLM says:")
            st.write(llm_response)

        with rag_tab:
            st.subheader("Try this:")

            selected_collection = st.selectbox(
                "Select a collection",
                available_collections,
                index=preselected_collection,
            )

            st.write(rag_response)
