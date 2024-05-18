import streamlit as st
import utils
from config import knowledge_base_name

with utils.get_weaviate_client() as client:
    st.header("Be a know-it-all 📚🤓")

    demo_tab, explanation_tab = st.tabs(["Demo", "What does it mean for me?"])

    with demo_tab:
        with st.expander("Teach me something"):
            pdf_path = st.text_input("Show me the path (URL) to knowledge (PDF) 📚")
            if pdf_path:
                utils.add_pdf(pdf_path)

        user_query = st.text_input("Now, ask me anything!")

        query_suffix = """
        Answer this in a 2-3, short, concise bullet points, using plain, non-technical language as much as possible.
        If an answer is not contained in the source material, just say 'I'm sorry, I don't know.' and nothing else. That's okay
        """

        if user_query:
            user_query = user_query + query_suffix

            st.subheader("🤖 says:")
            rag_response = utils.ask_rag(
                client=client,
                user_prompt=user_query,
                collection_name=knowledge_base_name,
            )
            st.write(rag_response)

    with explanation_tab:
        st.subheader("Instant knowledge!")
        st.write(
            "Your app be easily kept up-to-date, without complex & expensive re-training of models!"
        )
        with st.expander("Just like this guy..."):
            st.image("./assets/i-know-kung-fu.gif")
