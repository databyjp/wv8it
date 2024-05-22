import streamlit as st
import utils

with utils.get_weaviate_client() as client:

    intro_tab, demo_tab, explanation_tab = st.tabs(["Introduction", "Demo", "What does it mean for me?"])

    with intro_tab:
        st.header("Read minds 🧠🔮🧠")
        st.image("./assets/mind_reading.jpeg", width=500)

    with demo_tab:

        img, text = st.columns([1, 2])
        with img:
            st.image("./assets/etienne_headshot.png", use_column_width=True)

        with text:
            st.subheader("Ask 'Etienne'")
            st.write("⬅️ Etienne, our CTO.")
            st.write("He couldn't be here, but we can read his mind!")

        questions = [
            "Why did you build Weaviate in golang?",
            "What's multi-tenancy?",
            "What great about HNSW?",
            "What's locally adaptive quantization?",
            "Who's your favourite golfer?",
        ]
        question_caption = "Ask Etienne anything! (about Weaviate)"
        user_question = utils.type_or_select_question(questions=questions, question_caption=question_caption)

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
