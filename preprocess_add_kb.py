from weaviate import WeaviateClient
from weaviate.classes.config import Configure, Property, DataType
import utils
from config import knowledge_base_name, chunks_index_name, default_generative_config
from weaviate.util import generate_uuid5


def safe_delete_collection(wv_client: WeaviateClient, wv_coll_name: str) -> bool:
    if wv_client.collections.exists(wv_coll_name):
        user_input = input(
            f"Collection '{wv_coll_name}' exists. Delete (y / or any other key to cancel)? "
        )
        if user_input == "y":
            wv_client.collections.delete(wv_coll_name)
            print("Collection deleted.")
            return True
        else:
            print("Not deleted.")
            return False
    return True


client = utils.get_weaviate_client()

coll_name = knowledge_base_name

safe_delete_collection(client, coll_name)

if not client.collections.exists(coll_name):
    client.collections.create(
        coll_name,
        properties=[
            Property(name="title", data_type=DataType.TEXT),
            Property(name="url", data_type=DataType.TEXT, skip_vectorization=True),
            Property(name="chunk", data_type=DataType.TEXT),
            Property(name="chunk_no", data_type=DataType.INT),
        ],
        vectorizer_config=[
            Configure.NamedVectors.text2vec_ollama(
                name=chunks_index_name,
                model="snowflake-arctic-embed",
                api_endpoint="http://host.docker.internal:11434",
                vector_index_config=Configure.VectorIndex.hnsw(
                    quantizer=Configure.VectorIndex.Quantizer.bq()
                )
            ),
            # Configure.NamedVectors.text2vec_cohere(
            #     model="embed-multilingual-v3.0",
            #     name=chunks_index_name,
            #     vector_index_config=Configure.VectorIndex.hnsw(
            #         quantizer=Configure.VectorIndex.Quantizer.bq()
            #     )
            # )
        ],
        generative_config=default_generative_config
    )

utils.add_txt_local(
    client=client,
    title="Introducing Meta Llama 3 (2024 April 18)",
    collection_name=coll_name,
    txt_path="./assets/llama3.txt",
)

client.close()
