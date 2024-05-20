import distyll.utils
from weaviate.classes.config import Configure, Property, DataType
from weaviate.util import generate_uuid5
from pathlib import Path
import json
import distyll
import utils
from weaviate.collections.collection import Collection
from weaviate import WeaviateClient
from config import etienne_collection_name, chunks_index_name


utils.safe_delete_collection(utils.get_weaviate_client(), etienne_collection_name)


def get_or_create_collection(
    client: WeaviateClient, collection_name: str
) -> Collection:
    if not client.collections.exists(collection_name):
        collection = client.collections.create(
            name=collection_name,
            properties=[
                Property(name="title", data_type=DataType.TEXT),
                Property(name="chunk", data_type=DataType.TEXT),
                Property(name="chunk_no", data_type=DataType.INT),
                Property(name="url", data_type=DataType.TEXT, skip_vectorization=True),
            ],
            vectorizer_config=[
                Configure.NamedVectors.text2vec_ollama(
                    name="title_chunk",
                    source_properties=["title", "chunk"],
                    # model="snowflake-arctic-embed:33m",
                    model="snowflake-arctic-embed",
                    api_endpoint="http://host.docker.internal:11434",
                    vector_index_config=Configure.VectorIndex.hnsw(
                        quantizer=Configure.VectorIndex.Quantizer.bq()
                    ),
                ),
                Configure.NamedVectors.text2vec_ollama(
                    name=chunks_index_name,
                    source_properties=["chunk"],
                    # model="snowflake-arctic-embed:33m",
                    model="snowflake-arctic-embed",
                    api_endpoint="http://host.docker.internal:11434",
                    vector_index_config=Configure.VectorIndex.hnsw(
                        quantizer=Configure.VectorIndex.Quantizer.bq()
                    ),
                ),
            ],
            # generative_config=Configure.Generative.ollama(
            #     model="mistral:7b",
            #     api_endpoint="http://host.docker.internal:11434",
            # ),
            # generative_config=Configure.Generative.openai(
            #     model="gpt-4",
            # ),
            generative_config=Configure.Generative.cohere(
                model="command-r-plus",
            )
        )

    else:
        collection = client.collections.get(collection_name)
    return collection


def batch_insert(collection: Collection, json_files: list):
    with collection.batch.rate_limit(3000) as batch:
        for f in json_files:
            video_data_json = f.read_text()
            video_data_dict = json.loads(video_data_json)

            i = 0
            for transcript in video_data_dict["transcripts"]:
                chunks = distyll.utils.chunk_text(
                    transcript, method="words", token_length=100
                )
                for chunk in chunks:
                    try:
                        chunk_no = i
                        i += 1
                        batch.add_object(
                            properties={
                                "title": video_data_dict["title"],
                                "chunk": chunk,
                                "chunk_no": chunk_no,
                                "url": video_data_dict["yt_url"],
                            },
                            uuid=generate_uuid5(chunk),
                        )
                    except Exception as e:
                        print(f"Error: {e}")
                        continue


my_client = utils.get_weaviate_client()

# Add Etienne talks to Weaviate
etienne_collection = get_or_create_collection(
    client=my_client, collection_name=etienne_collection_name
)
etienne_json_path = Path("./dl_dir/etienne")
etienne_json_files = etienne_json_path.glob("*.json")

batch_insert(collection=etienne_collection, json_files=etienne_json_files)

my_client.close()
