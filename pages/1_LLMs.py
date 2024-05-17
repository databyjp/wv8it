import streamlit as st
import utils
from config import wiki_collection_name

client = utils.get_weaviate_client()

st.subheader("LLMs are amazing!")

user_question = st.text_input("Ask a question")

if user_question:
    llm_response = utils.ask_llm(user_question)
    rag_response = utils.ask_rag(client=client, user_prompt=user_question, collection_name=wiki_collection_name, target_vector="chunk")

    llm_tab, rag_tab = st.tabs(["LLM", "LLM+"])
    with llm_tab:
        st.subheader("LLM says:")
        st.write(llm_response)

    with rag_tab:
        st.subheader("But you can do more...")
        st.write(rag_response)
