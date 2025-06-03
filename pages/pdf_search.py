import streamlit as st
from pathlib import Path
from PIL import Image
import base64
from io import BytesIO
from utils import (
    render_svg_file,
    get_weaviate_client
)
from weaviate import WeaviateClient
from weaviate.classes.query import MetadataQuery
from weaviate.classes.generate import GenerativeParameters, GenerativeConfig
from embedkit import EmbedKit
from embedkit.classes import Model, CohereInputType
import os

collection_name = "SlideDeck"

# Initialize session state for query
if 'query' not in st.session_state:
    st.session_state.query = ""

with get_weaviate_client() as client:

    st.title("Weaviate + Multimodal Image Search")
    st.markdown(
        "Search for PDF pages in natural language with a multi-modal vectorizer"
    )

    kit = EmbedKit.cohere(
        api_key=os.getenv("COHERE_API_KEY"),
        model=Model.Cohere.EMBED_V4_0,
        image_batch_size=8,
        text_input_type=CohereInputType.SEARCH_QUERY
    )

    # Function to perform search
    def search_images(query, weaviate_client: WeaviateClient, top_k=6):
        pdfs = weaviate_client.collections.get(name=collection_name)
        query_vector = kit.embed_text(query).objects[0].embedding

        response = pdfs.query.near_vector(
            near_vector=query_vector,
            target_vector="cohere",
            return_properties=["image", "page", "filepath"],
            limit=top_k,
            return_metadata=MetadataQuery(distance=True),
        )

        return response


    # Function to perform rag
    def mm_rag(query, rag_query, weaviate_client: WeaviateClient, top_k=6):
        pdfs = weaviate_client.collections.get(name=collection_name)
        query_vector = kit.embed_text(query).objects[0].embedding

        response = pdfs.generate.near_vector(
            near_vector=query_vector,
            target_vector="cohere",
            limit=top_k,
            return_metadata=MetadataQuery(distance=True),
            # generative_provider=GenerativeConfig.anthropic(model="claude-sonnet-4-20250514"),
            generative_provider=GenerativeConfig.openai(model="gpt-4o"),
            grouped_task=GenerativeParameters.grouped_task(
                prompt=rag_query,
                image_properties=["image"]
            )
        )

        return response.generative.text

    # Function to reset query
    def reset_query():
        st.session_state.query = ""

    # Create the main settings section
    st.subheader("🔍 Search Settings")

    # Create a two-column layout for the search input and example queries
    search_col, example_col = st.columns([1, 1])

    with search_col:
        # Create a single column for the search input
        query = st.text_input("Enter your query (or select an example)", key="query")

        # Buttons below the query
        button_col1, button_col2 = st.columns(2)
        with button_col1:
            search_button = st.button("Search", type="primary")
        with button_col2:
            reset_button = st.button("Reset", on_click=reset_query)

        # Number of results dropdown
        num_results = st.selectbox("Number of results", options=[2, 4, 6, 8], index=1)

    with example_col:
        st.write("Example queries")
        example_queries = [
            "Weaviate cluster architecture",
            "HNSW quantization",
            "Vector search explanation",
            "Vector DBs and spongebob squarepants",
        ]

        # Function to set example query
        def set_example_query(example):
            st.session_state.query = example

        for example in example_queries:
            if st.button(example[:40] + "..." if len(example) > 40 else example,
                        on_click=set_example_query,
                        args=(example,),
                        key=f"example_{example}",
                        type="primary"):
                search_button = True

    # Display the SVG logo with specified dimensions
    st.write(
        "Powered by:", render_svg_file(
            "assets/weaviate-logo-square-dark.svg", width="80px", height="80px"
        ),
        unsafe_allow_html=True,
    )

    # Main area for displaying results
    if (search_button or len(query) > 0) and query.strip():
        with st.spinner("Searching for images..."):
            results = search_images(query, weaviate_client=client, top_k=num_results)

        st.subheader(f"Results for: '{query}'")

        # Create a grid layout for the results
        cols = 2
        rows = (num_results + cols - 1) // cols

        for row in range(rows):
            columns = st.columns(cols)
            for col in range(cols):
                idx = row * cols + col
                if idx < len(results.objects):
                    result = results.objects[idx]
                    with columns[col]:
                        try:
                            # Get the base64 image data from the blob
                            image_data = result.properties["image"]
                            # Decode base64 to bytes
                            image_bytes = base64.b64decode(image_data)
                            # Convert bytes to image
                            img = Image.open(BytesIO(image_bytes))
                            st.image(
                                img, caption=f"File: {result.properties['filepath']}, page: {result.properties['page']}, vector distance: {result.metadata.distance:.2f}"
                            )
                        except Exception as e:
                            st.error(f"Error loading image: {str(e)}")

        st.subheader("Multimodal RAG")
        default_rag_query = f"What do these slides tell us? The search query was: {query}"

        # Add text input for custom RAG query
        custom_rag_query = st.text_input(
            "Customize RAG query (optional)",
            value=default_rag_query,
            help="Modify the query to get different insights from the slides"
        )

        # Use custom query if provided, otherwise use default
        rag_query = custom_rag_query if custom_rag_query.strip() else default_rag_query

        # Add a button for RAG
        if st.button("Generate RAG Response", type="primary"):
            if (len(rag_query.strip()) > 0):
                with st.spinner("Generating RAG response... This may take a few moments."):
                    rag_response_txt = mm_rag(
                        query,
                        rag_query,
                        weaviate_client=client,
                        top_k=num_results
                    )

                st.write(f"Response for: '{rag_query}'")
                st.write(f"{rag_response_txt}")


    elif search_button and not query.strip():
        st.error("Please enter a search query before clicking the Search button.")
