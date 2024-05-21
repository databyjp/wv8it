import streamlit as st
import utils
from config import wiki_name, chunks_index_name
from weaviate.classes.query import Filter

with utils.get_weaviate_client() as client:
    st.header("Lightning ⚡️ fast vector searches")

    demo_tab, explanation_tab = st.tabs(["Demo", "What does it mean for me?"])

    user_query = utils.ask_llm(
        "Generate a random search string for me, just a few words please."
    )

    with demo_tab:
        search_responses = utils.search_comparison(
            client=client, collection_name=wiki_name, user_query=user_query
        )

        st.subheader("Search speed comparison:")

        st.write("For a randomised search query, how long does a vector search take?")

        coll = client.collections.get(wiki_name)

        count = coll.aggregate.over_all(total_count=True).total_count

        st.write(f"Dataset: {count} objects")

        col1, col2 = st.columns(2)

        with col1:
            search_time = round(search_responses["flat"][1], 5)
            st.markdown(f"##### Brute force search: `{search_time}`s")

        with col2:
            if chunks_index_name in search_responses.keys():
                search_time = round(search_responses[chunks_index_name][1], 5)
                st.markdown(f"##### Approximate nearest neighbor (ANN) search: `{search_time}`s")

        st.write("As the dataset grows, the difference in search time will become more pronounced.")
        st.write("For a dataset 100x the size: linear search would take 100x longer, while ANN would take a few times longer.")

    with explanation_tab:
        points = [
            "- ##### Scale datasets to hundreds of millions or more",
            "- ##### RAG remains fast and accurate",
        ]

        utils.explain_meaning(points=points)
