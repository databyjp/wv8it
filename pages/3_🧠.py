import streamlit as st
import utils

client = utils.get_weaviate_client()

st.subheader("Mind reading")

user_question = st.text_input("What would Etienne say on this topic?")

if user_question:
    search_response, gen_response = utils.ask_etienne(client=client, user_question=user_question)

    st.subheader("Mind reading:")
    st.write(gen_response.generated)

    st.subheader("How did we do this?")
    with st.expander("Look behind the curtain"):
        for obj in search_response.objects:
            st.write(obj.properties["title"])
            st.write(obj.properties["chunk"])
