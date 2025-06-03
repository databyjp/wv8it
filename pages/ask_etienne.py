import streamlit as st
import utils

with utils.get_weaviate_client() as client:
    demo_tab, explanation_tab = st.tabs(["Demo", "What does it mean for me?"])

    with demo_tab:
        img, text = st.columns([1, 2])
        with img:
            st.image("./assets/etienne_headshot.png", use_container_width=True)

        with text:
            st.subheader("Ask 'Etienne'")
            st.write("⬅️ Etienne, our CTO.")
            st.write("Let's ask the man who knows about all things Weaviate!")

        questions = [
            "Why are vector databases so popular?",
            "What's great about vector search?",
            "What's great about HNSW?",
            "What's multi-tenancy?",
            "Why did you build Weaviate in golang?",
            "Who's your favourite golfer?",
        ]
        question_caption = "Ask Etienne anything! (about Weaviate)"
        user_question = utils.type_or_select_question(
            questions=questions, question_caption=question_caption
        )

        if user_question:
            search_response, gen_response = utils.ask_etienne(
                client=client, user_question=user_question
            )

            st.subheader("💬 Etinne (probably) says:")
            st.write(gen_response.generated)

    with explanation_tab:
        points = [
            "- ##### Capture internal & external expertise",
            "- ##### Scale & access expertise from anywhere",
            "- ##### Enable self-service support & knowledge discovery",
        ]

        utils.explain_meaning(points=points)

        if user_question and search_response:
            utils.show_search_results(search_response=search_response)
