import streamlit as st
import utils

with utils.get_weaviate_client() as client:
    st.header("Read minds 🧠🔮🧠")

    demo_tab, explanation_tab = st.tabs(["Demo", "What does it mean for me?"])

    with demo_tab:
        img, text = st.columns([1, 2])
        with img:
            st.image("./assets/etienne_headshot.png", use_column_width=True)

        with text:
            st.subheader("Ask 'Etienne'")
            st.write("⬅️ Etienne, our CTO.")
            st.write("He couldn't be here, but we can read his mind!")

        # type_own_question = "Or, type your own question"
        # questions = [
        #     "Why did you build Weaviate in golang?",
        #     "What's multi-tenancy?",
        #     "What great about HNSW?",
        #     "What's locally adaptive quantization?",
        #     "Who's your favourite golfer?",
        #     type_own_question,
        # ]
        # selected_question = st.selectbox(
        #     "Select a question", questions, index=len(questions) - 1
        # )

        # if selected_question == type_own_question:
        #     user_question = st.text_input("Ask Etienne anything! (about Weaviate)")
        # else:
        #     user_question = selected_question

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
