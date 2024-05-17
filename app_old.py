import streamlit as st
import weaviate
from weaviate.classes.query import Filter, MetadataQuery
import utils
import os


MAX_N_CHUNKS = 15

st.set_page_config(layout="wide")

if "generated_response" not in st.session_state:
    st.session_state.generated_response = ""
if "search_response" not in st.session_state:
    st.session_state.search_response = ""

img_col, _, _ = st.columns([10, 30, 30])
with img_col:
    st.image("assets/weaviate-logo-dark-name-transparent-for-light.png")
st.header("Get smarter with RAG")

video_options = utils.ETIENNE_COLLECTION

overview, why, search, multimodal, ask_etienne = st.tabs(
    ["👋 Overview", "🧐 Why Vector DBs?", "🔎 Search!", "🏞️ Multimodal", "💬 Ask Etienne"]
)

with overview:
    st.markdown("## Give your apps superpowers")

client = utils.get_weaviate_client()

chunks = client.collections.get("TextChunk")


with ask_etienne:
    st.subheader("Ask Etienne")

    st.subheader("Available videos:")
    a, b, c = st.columns(3)
    columns = [a, b, c]

    for i, video in enumerate(video_options):
        col_index = i % 3
        with columns[col_index]:
            st.video(data=video)
            title = video_title_dict[video]
            st.write(title)

    video_selection = st.selectbox("Select a video", options=title_video_dict.keys())
    youtube_url = title_video_dict[video_selection]
    st.markdown("#### Ask the video anything!")
    user_question = st.text_input("What do you want to know?")

with tab2:
    st.subheader("How does it all work?")

if len(user_question) > 3:
    with tab1:
        with st.expander("Raw data found:"):
            search()
            st.write(st.session_state.search_response)

        #     response = chunks.query.near_text(
        #         query=user_question,
        #         filters=Filter.by_property("url").equal(youtube_url),
        #         limit=MAX_N_CHUNKS,
        #         target_vector="chunk"
        #     )

        #     for resp_obj in response.objects:
        #         st.write(resp_obj)

        # prompt = f"""
        # Answer the question: {user_question}.
        # Feel free to use the text contained here.
        # The answer should be well-written, succinct and thoughtful, using plain language even if the source material is technical.
        # If there is no information, say 'The source material does not say.'.
        # """

        # response = chunks.generate.near_text(
        #     query=user_question,
        #     filters=Filter.by_property("url").equal(youtube_url),
        #     limit=MAX_N_CHUNKS,
        #     grouped_task=prompt,
        # )

        # # for resp_obj in response.objects:
        # #     st.write(resp_obj)

        # st.write(response.generated)

        submit_button = st.button("Generate answer", on_click=generate)
        st.write(st.session_state.generated_response)

    with tab2:
        with st.expander("Code snippet:"):
            st.code(
                '''
                prompt = f"""
                Answer the question: {user_question}.
                Feel free to use the text contained here.
                The answer should be well-written, succinct and thoughtful, using plain language even if the source material is technical.
                If there is no information, say 'The source material does not say.'.
                """,

                response = chunks.generate.near_text(
                    filters=Filter.by_property("url").equal(youtube_url),
                    query=user_question,
                    limit=MAX_N_CHUNKS,
                    grouped_task=prompt
                )

                ''',
                language="python",
            )
else:
    with tab2:
        st.write("Run a search first and come back! :)")
