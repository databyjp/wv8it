from datasets import load_dataset
from weaviate import WeaviateClient
import os
from weaviate.classes.config import Configure, Property, DataType
from weaviate.util import generate_uuid5
from tqdm import tqdm
import utils
from config import wiki_name, chunks_index_name, default_generative_config

client = utils.get_weaviate_client()

coll_name = wiki_name

utils.safe_delete_collection(client, coll_name)

if not client.collections.exists(coll_name):
    client.collections.create(
        name=coll_name,
        properties=[
            Property(name="title", data_type=DataType.TEXT),
            Property(name="text", data_type=DataType.TEXT),
            Property(name="url", data_type=DataType.TEXT, skip_vectorization=True),
            Property(
                name="cohere_id", data_type=DataType.TEXT, skip_vectorization=True
            ),
            Property(name="chunk_no", data_type=DataType.INT),
            Property(name="lang", data_type=DataType.TEXT),
        ],
        vectorizer_config=[
            Configure.NamedVectors.text2vec_cohere(
                model="embed-multilingual-v3.0",
                name=chunks_index_name,
                vector_index_config=Configure.VectorIndex.hnsw(
                    quantizer=Configure.VectorIndex.Quantizer.bq()
                ),
                source_properties=["title", "text"],
            ),
            Configure.NamedVectors.text2vec_cohere(
                model="embed-multilingual-v3.0",
                name="flat",
                vector_index_config=Configure.VectorIndex.flat(),
                source_properties=["title", "text"],
            ),
        ],
        generative_config=default_generative_config
    )

wiki_coll = client.collections.get(coll_name)

import_sets = [
    ("simple", 550000),  # Simple English Wiki subset
    ("fr", 150000),  # French Wikipedia
    ("ko", 150000),  # Korean Wikipedia
    ("nl", 150000),  # Dutch Wikipedia
]

for lang, max_rows in import_sets:
    docs = load_dataset(
        "Cohere/wikipedia-2023-11-embed-multilingual-v3", lang, split="train"
    )

    docs.shuffle()

    with wiki_coll.batch.fixed_size(1000) as batch:
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
                vector={
                    chunks_index_name: doc["emb"],
                    "flat": doc["emb"],
                },
            )

            if batch.number_errors > 100:
                print("Too many errors, exiting")
                break

            if i + 1 == max_rows:
                print("Finished! Exiting")
                break

client.close()
