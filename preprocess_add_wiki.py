from datasets import load_dataset
from weaviate import WeaviateClient
import os
from weaviate.classes.config import Configure, Property, DataType
from weaviate.util import generate_uuid5
from tqdm import tqdm
import utils
from config import wiki_collection_name

lang = "simple"  # Use the Simple English Wikipedia subset
docs = load_dataset(
    "Cohere/wikipedia-2023-11-embed-multilingual-v3", lang, split="train"
)

MAX_ROWS = 50000


my_coherekey = os.getenv("COHERE_APIKEY")

client = utils.get_weaviate_client(port=80)

assert client.is_ready()

coll_name = wiki_collection_name


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


safe_delete_collection(client, coll_name)


client.collections.create(
    name=coll_name,
    properties=[
        Property(name="cohere_id", data_type=DataType.TEXT),
        Property(name="title", data_type=DataType.TEXT),
        Property(name="text", data_type=DataType.TEXT),
        Property(name="url", data_type=DataType.TEXT),
    ],
    vectorizer_config=[
        Configure.NamedVectors.text2vec_cohere(
            model="embed-multilingual-v3.0",
            name="chunk",
            vector_index_config=Configure.VectorIndex.hnsw(),
            source_properties=["title", "text"],
        ),
        # Configure.NamedVectors.text2vec_cohere(
        #     model="embed-multilingual-v3.0",
        #     name="hnsw_bq",
        #     vector_index_config=Configure.VectorIndex.hnsw(
        #         quantizer=Configure.VectorIndex.Quantizer.bq()
        #     ),
        # ),
        # Configure.NamedVectors.text2vec_cohere(
        #     model="embed-multilingual-v3.0",
        #     name="flat",
        #     vector_index_config=Configure.VectorIndex.flat(),
        # ),
        # Configure.NamedVectors.text2vec_cohere(
        #     model="embed-multilingual-v3.0",
        #     name="flat_bq",
        #     vector_index_config=Configure.VectorIndex.flat(
        #         quantizer=Configure.VectorIndex.Quantizer.bq()
        #     ),
        # ),
    ],
    generative_config=Configure.Generative.openai()
)


wiki_coll = client.collections.get(coll_name)

with wiki_coll.batch.fixed_size(1000) as batch:
    for i, doc in enumerate(tqdm(docs)):
        properties = {k: doc[k] for k in doc.keys() if k != "emb"}
        properties["cohere_id"] = properties.pop("_id")
        batch.add_object(
            properties=properties, uuid=generate_uuid5(doc["_id"]), vector=doc["emb"]
        )

        if batch.number_errors > 100:
            print("Too many errors, exiting")
            break

        if i + 1 == MAX_ROWS:
            print("Finished! Exiting")
            break

client.close()
