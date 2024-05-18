from datasets import load_dataset
from weaviate import WeaviateClient
import os
from weaviate.classes.config import Configure, Property, DataType
from weaviate.util import generate_uuid5
from tqdm import tqdm
import utils
from config import wiki_name, wiki_index_name


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

coll_name = wiki_name

safe_delete_collection(client, coll_name)

if not client.collections.exists(coll_name):
    client.collections.create(
        name=coll_name,
        properties=[
            Property(name="title", data_type=DataType.TEXT),
            Property(name="text", data_type=DataType.TEXT),
            Property(name="url", data_type=DataType.TEXT, skip_vectorization=True),
            Property(name="cohere_id", data_type=DataType.TEXT, skip_vectorization=True),
            Property(name="chunk_no", data_type=DataType.INT),
            Property(name="lang", data_type=DataType.TEXT),
        ],
        vectorizer_config=[
            Configure.NamedVectors.text2vec_cohere(
                model="embed-multilingual-v3.0",
                name=wiki_index_name,
                vector_index_config=Configure.VectorIndex.hnsw(
                    quantizer=Configure.VectorIndex.Quantizer.bq()
                ),
                source_properties=["title", "text"],
            ),
        ],
        generative_config=Configure.Generative.cohere(
            model="command-r-plus",
        ),
    )

wiki_coll = client.collections.get(coll_name)

# import_sets = [
#     ("simple", 1000000),  # Simple English Wiki subset
#     ("fr", 50000),  # French Wikipedia
#     ("ko", 50000),  # Korean Wikipedia
#     ("nl", 50000),  # Dutch Wikipedia
# ]

import_sets = [
    ("simple", 100),  # Simple English Wiki subset
    ("fr", 50),  # French Wikipedia
    ("ko", 50),  # Korean Wikipedia
    ("nl", 50),  # Dutch Wikipedia
]

for lang, max_rows in import_sets:
    docs = load_dataset(
        "Cohere/wikipedia-2023-11-embed-multilingual-v3", lang, split="train"
    )

    with wiki_coll.batch.fixed_size(2000) as batch:
        for i, doc in enumerate(tqdm(docs)):
            properties = {k: doc[k] for k in doc.keys() if k != "emb"}
            properties["cohere_id"] = properties.pop("_id")
            properties["lang"] = lang
            try:
                properties["chunk_no"] = int(properties["cohere_id"].split("_")[-1])
            except ValueError:
                properties["chunk_no"] = -1

            batch.add_object(
                properties=properties,
                uuid=generate_uuid5(doc["_id"]),
                vector={wiki_index_name: doc["emb"]},
            )

            if batch.number_errors > 100:
                print("Too many errors, exiting")
                break

            if i + 1 == max_rows:
                print("Finished! Exiting")
                break

client.close()
