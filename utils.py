import os
import distyll.utils
import streamlit as st
import weaviate
from weaviate import WeaviateClient
import cohere
import ollama
from config import (
    etienne_collection_name,
    chunks_index_name,
    MAX_N_CHUNKS,
    ETIENNE_VIDEOS,
)
from weaviate.classes.query import Filter
from typing import List, Literal
import distyll
from weaviate.util import generate_uuid5


def get_weaviate_client(port: int = 8080, grpc_port: int = 50051) -> WeaviateClient:
    openai_apikey = os.getenv("OPENAI_APIKEY")
    cohere_apikey = os.getenv("COHERE_APIKEY")

    client = weaviate.connect_to_local(
        port=port,
        grpc_port=grpc_port,
        headers={
            "X-OpenAI-Api-Key": openai_apikey,
            "X-Cohere-Api-Key": cohere_apikey,
        },
    )
    return client


def ask_llm(
    user_prompt: str,
    search_queries_only=False,
    provider: Literal["ollama", "cohere"] = "cohere",
) -> str:
    if provider == "cohere":
        cohere_apikey = os.getenv("COHERE_APIKEY")
        co = cohere.Client(api_key=cohere_apikey)

        response = co.chat(
            model="command-r-plus",
            message=user_prompt,
            search_queries_only=search_queries_only,
        )

        if search_queries_only:
            return response.search_queries[0].text
        else:
            return response.text
    if provider == "ollama":
        response = ollama.chat(
            model="mistral:7b",
            messages=[
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
        )
        return response["message"]["content"]


def ask_rag(
    client: WeaviateClient,
    user_prompt: str,
    collection_name: str,
    target_vector: str = "default",
    limit=MAX_N_CHUNKS,
):
    collection = client.collections.get(collection_name)

    try:
        search_query = ask_llm(user_prompt=user_prompt, search_queries_only=True)
    except Exception as e:
        search_query = user_prompt

    user_prompt += " Answer the question if possible from the provided text snippets. If not, just say 'I'm not sure.' - that's totally fine."

    response = collection.generate.hybrid(
        query=search_query,
        limit=limit,
        grouped_task=user_prompt,
        target_vector=target_vector,
    )

    return response


def video_search(
    client: WeaviateClient,
    collection_name: str,
    user_question: str,
    limit: int = MAX_N_CHUNKS,
):
    collection = client.collections.get(collection_name)

    search_response = collection.query.near_text(
        query=user_question,
        filters=Filter.by_property("url").contains_any(ETIENNE_VIDEOS),
        limit=limit,
        target_vector=chunks_index_name,
    )
    return search_response


def video_rag(
    client: WeaviateClient,
    collection_name: str,
    search_query: str,
    prompt: str,
    limit: int = MAX_N_CHUNKS,
):
    collection = client.collections.get(collection_name)

    gen_response = collection.generate.near_text(
        query=search_query,
        filters=Filter.by_property("url").contains_any(ETIENNE_VIDEOS),
        limit=limit,
        grouped_task=prompt,
        target_vector=chunks_index_name,
    )
    return gen_response


def ask_etienne(client: WeaviateClient, user_question: str, limit: int = MAX_N_CHUNKS):
    search_response = video_search(
        client=client,
        collection_name=etienne_collection_name,
        user_question=user_question,
        limit=limit,
    )

    prompt = f"""
    Answer the question: {user_question}.
    Feel free to use the text contained here, which are text snippets from interviews or talks with Etienne about Weaviate.
    Note the transcript might mistake 'Weaviate' for some variations.
    The answer should be in 2-4 short bullet points, using plain language even if the source material is technical.
    Answer in a similar voice to the source material, as if Etienne were speaking.
    If there is no information, say 'Sorry, I'm not sure what Etienne would say about that.' That's perfectly fine.
    """

    if "golf" in user_question:
        prompt += " Etienne's favorite golfer is Rory McIlroy. Etienne is a big fan of Rory's swing, and has been a big fan of his for a while now."

    gen_response = video_rag(
        client=client,
        collection_name=etienne_collection_name,
        search_query=user_question,
        prompt=prompt,
        limit=limit,
    )

    return (search_response, gen_response)


def search(
    client: WeaviateClient,
    collection_name: str,
    user_query: str,
    target_vector: str = "default",
    limit: int = MAX_N_CHUNKS,
):
    collection = client.collections.get(collection_name)

    search_response = collection.query.near_text(
        query=user_query, limit=limit, target_vector=target_vector
    )
    return search_response


def timed_search(
    client: WeaviateClient,
    collection_name: str,
    user_query: str,
    target_vector: str = "default",
    limit: int = MAX_N_CHUNKS,
):
    import time

    start = time.time()
    search_response = search(
        client=client,
        collection_name=collection_name,
        user_query=user_query,
        target_vector=target_vector,
        limit=limit,
    )
    end = time.time()

    search_time = end - start

    return search_response, search_time


def search_comparison(
    client: WeaviateClient,
    collection_name: str,
    user_query: str,
    indexes: List[str] = ["chunk"],
    limit: int = MAX_N_CHUNKS,
):
    search_results = {}

    for i in indexes:
        search_response, search_time = timed_search(
            client=client,
            collection_name=collection_name,
            user_query=user_query,
            target_vector=i,
            limit=limit,
        )
        search_results[i] = (search_response, search_time)

    return search_results


def add_pdf(pdf_url: str):
    import distyll.db

    client = get_weaviate_client()

    if "arxiv" in pdf_url:
        distyll.db.add_arxiv_to_db(client=client, arxiv_url=pdf_url)
    else:
        distyll.db.add_pdf_to_db(client=client, pdf_url=pdf_url)

    client.close()


def explain_meaning(points: List[str], state_key: str):
    st.subheader("With this, you could...")

    if state_key not in st.session_state:
        st.session_state[state_key] = 0

    show_more_col, button_col = st.columns([4, 1])

    def show_more():
        if st.session_state[state_key] < len(points):
            with show_more_col:
                for i in range(st.session_state[state_key] + 1):
                    st.markdown(points[i])
                st.session_state[state_key] += 1
        else:
            with show_more_col:
                for i in range(len(points)):
                    st.markdown(points[i])

    with button_col:
        if st.button("Show more"):
            show_more()


def add_txt_local(
    client: WeaviateClient,
    title: str,
    collection_name: str,
    txt_path: str,
    token_length: int = 100,
):
    with open(txt_path, "r") as f:
        src_txt = f.read()

    coll = client.collections.get(collection_name)

    chunks = distyll.utils.chunk_text(
        src_txt, method="words", token_length=token_length
    )

    coll.data.delete_many(where=Filter.by_property("url").equal(txt_path))

    for i, chunk in enumerate(chunks):
        obj_uuid = generate_uuid5(txt_path + str(i))

        coll.data.insert(
            properties={
                "title": title,
                "url": txt_path,
                "chunk": chunk,
                "chunk_no": 1,
            },
            uuid=obj_uuid,
        )
