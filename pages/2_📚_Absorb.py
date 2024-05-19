import streamlit as st
import utils
from config import knowledge_base_name, chunks_index_name

state_key = "knowledge_counter"

with utils.get_weaviate_client() as client:
    st.header("Be a know-it-all 📚🤓")

    demo_tab, teach_tab, explanation_tab = st.tabs(
        ["Demo", "Teach me something", "What does it mean for me?"]
    )

    with demo_tab:
        user_query = st.text_input("Ask me anything!")

        query_suffix = """
        Answer this in a 2-5, short, concise bullet points, preferably using plain, not very technical language as much as possible.
        If an answer is not contained in the source material, just say 'I'm sorry, I don't know.' and nothing else. That's okay
        """

        if user_query:
            user_query = user_query + query_suffix

            st.subheader("🤖 says:")
            rag_response = utils.ask_rag(
                client=client,
                user_prompt=user_query,
                collection_name=knowledge_base_name,
                target_vector=chunks_index_name,
            )
            st.write(rag_response.generated)

    with teach_tab:
        pdf_path = st.text_input("Show me the path (URL) to knowledge (PDF) 📚")
        with st.expander("What will happen here?"):
            st.markdown(
                """
                - Extract text from the PDF
                - Chunk the text into smaller pieces
                - Add the chunks to the knowledge store
                """
            )

        if pdf_path:
            utils.add_pdf(pdf_path)

    with explanation_tab:
        points = [
            "- ##### Leverage any existing knowledge source",
            "- ##### Easily keep your knowledge store up-to-date",
            "- ##### No need for complex & expensive re-training of models",
        ]

        utils.explain_meaning(points=points, state_key=state_key)

        with st.expander("Just like this guy..."):
            st.image("./assets/i-know-kung-fu.gif", use_column_width=True)
