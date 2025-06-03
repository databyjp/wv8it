import streamlit as st
import utils
from config import wiki_name, chunks_index_name
from weaviate.classes.query import Filter
import time

st.subheader("Search Speed Comparison")

st.markdown("""
    This demo compares the performance of brute force search versus HNSW index search.
""")

with utils.get_weaviate_client() as client:
    coll = client.collections.get(wiki_name)
    count = coll.aggregate.over_all(total_count=True).total_count

    st.info(f"📊 Dataset size: {count:,} objects")

    if st.button("🚀 Run Search Speed Demo", type="primary"):
        user_query = utils.ask_llm(
            "Generate a random search string for me, just a few words please."
        )

        # Initialize results containers
        hnsw_times = []
        flat_times = []

        # Run flat search 3 times
        st.markdown(f"### 🐢 Brute Force Search - {count} objects")
        flat_progress = st.progress(0)
        flat_status = st.empty()
        for i in range(3):
            search_responses = utils.search_comparison(
                client=client, collection_name=wiki_name, user_query=user_query
            )
            flat_times.append(search_responses["flat"][1])
            flat_progress.progress((i + 1) / 3)
            flat_status.write(f"Run {i+1}/3 completed")

        # Run HNSW search 3 times
        st.markdown(f"### ⚡ HNSW Index Search - {count} objects")
        hnsw_progress = st.progress(0)
        hnsw_status = st.empty()
        for i in range(3):
            search_responses = utils.search_comparison(
                client=client, collection_name=wiki_name, user_query=user_query
            )
            if chunks_index_name in search_responses.keys():
                hnsw_times.append(search_responses[chunks_index_name][1])
            hnsw_progress.progress((i + 1) / 3)
            hnsw_status.write(f"Run {i+1}/3 completed")

        # Calculate averages
        avg_flat_time = round(sum(flat_times) / len(flat_times), 5)
        avg_hnsw_time = round(sum(hnsw_times) / len(hnsw_times), 5)

        # Display results
        st.markdown("### 📊 Results")
        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                label="Brute Force Search",
                value=f"{avg_flat_time}s",
                delta="0%, baseline",
                delta_color="normal"
            )
            st.markdown("**Individual run times:**")
            for i, t in enumerate(flat_times):
                st.markdown(f"- Run {i+1}: `{round(t, 5)}s`")

        with col2:
            if hnsw_times:
                st.metric(
                    label="HNSW Index Search",
                    value=f"{avg_hnsw_time}s",
                    delta=f"{round((avg_flat_time - avg_hnsw_time) / avg_flat_time * 100, 1)}% faster",
                    delta_color="normal"
                )
                st.markdown("**Individual run times:**")
                for i, t in enumerate(hnsw_times):
                    st.markdown(f"- Run {i+1}: `{round(t, 5)}s`")

        st.markdown("""
            ---
            ### 💡 Key Insights
            - As the dataset grows, the performance difference becomes more pronounced
            - For a dataset 100x larger:
                - Brute force search would take ~100x longer
                - HNSW search would only take a few times longer
        """)
