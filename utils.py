import os
import weaviate
from weaviate import WeaviateClient
import cohere
from config import (
    etienne_collection_name,
    etienne_index_name,
    MAX_N_CHUNKS,
    ETIENNE_COLLECTION,
)
from weaviate.classes.query import Filter
from weaviate.collections.collection import Collection
from typing import List, Tuple


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


def ask_llm(user_prompt: str, search_queries_only=False) -> str:
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


def ask_rag(client: WeaviateClient, user_prompt: str, collection_name: str, target_vector: str = "default", limit=5) -> str:
    collection = client.collections.get(collection_name)

    response = collection.generate.near_text(
        query=ask_llm(user_prompt=user_prompt, search_queries_only=True),
        limit=limit,
        grouped_task=user_prompt,
        target_vector=target_vector
    )

    return response.generated


def video_search(client: WeaviateClient, collection_name: str, user_question: str, limit: int = MAX_N_CHUNKS):
    collection = client.collections.get(collection_name)

    search_response = collection.query.near_text(
        query=user_question,
        filters=Filter.by_property("url").contains_any(ETIENNE_COLLECTION),
        limit=limit,
        target_vector=etienne_index_name,
    )
    return search_response


def video_rag(
    client: WeaviateClient, collection_name: str, search_query: str, prompt: str, limit: int = MAX_N_CHUNKS
):
    collection = client.collections.get(collection_name)

    gen_response = collection.generate.near_text(
        query=search_query,
        filters=Filter.by_property("url").contains_any(ETIENNE_COLLECTION),
        limit=limit,
        grouped_task=prompt,
        target_vector=etienne_index_name,
    )
    return gen_response


def ask_etienne(client: WeaviateClient, user_question: str, limit: int = MAX_N_CHUNKS):

    search_response = video_search(
        client=client, collection_name=etienne_collection_name, user_question=user_question, limit=limit
    )

    prompt = f"""
    Answer the question: {user_question}.
    Feel free to use the text contained here.
    The answer should be well-written, succinct and thoughtful, using plain language even if the source material is technical.
    If there is no information, say 'The source material does not say.'.
    """

    gen_response = video_rag(
        client=client, collection_name=etienne_collection_name, search_query=user_question, prompt=prompt, limit=limit
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
    indexes: List[str] = ["hnsw", "hnsw_bq", "flat", "flat_bq"],
    limit: int = MAX_N_CHUNKS,
):
    search_results = {}

    indexes = ["hnsw", "hnsw_bq", "flat", "flat_bq"]

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
