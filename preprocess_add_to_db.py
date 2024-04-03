import distyll.utils
import weaviate
from weaviate.classes.config import Configure, Property, DataType
from weaviate.util import generate_uuid5
import os
from pathlib import Path
import json
import distyll

openai_apikey = os.getenv("OPENAI_APIKEY")

client = weaviate.connect_to_local(
    headers={"X-OpenAI-Api-Key": openai_apikey}
)

collection_name = "TextChunk"

if not client.collections.exists(collection_name):
    collection = client.collections.create(
        name="TextChunk",
        properties=[
            Property(name="title", data_type=DataType.TEXT),
            Property(name="chunk", data_type=DataType.TEXT),
            Property(name="chunk_no", data_type=DataType.INT),
            Property(name="url", data_type=DataType.TEXT, skip_vectorization=True),
        ],
        vectorizer_config=[
            Configure.NamedVectors.text2vec_openai(
                name="title",
                source_properties=["title"],
                vector_index_config=Configure.VectorIndex.hnsw(
                    quantizer=Configure.VectorIndex.Quantizer.bq()
                )
            ),
            Configure.NamedVectors.text2vec_openai(
                name="chunk",
                source_properties=["chunk"],
                vector_index_config=Configure.VectorIndex.hnsw(
                    quantizer=Configure.VectorIndex.Quantizer.bq()
                )
            )
        ],
        generative_config=Configure.Generative.openai(),
    )

else:
    collection = client.collections.get(collection_name)


json_path = Path("./dl_dir")
json_files = json_path.glob("*.json")

with collection.batch.rate_limit(3000) as batch:
    for f in json_files:
        video_data_json = f.read_text()
        video_data_dict = json.loads(video_data_json)

        i = 0
        for transcript in video_data_dict["transcripts"]:
            chunks = distyll.utils.chunk_text(transcript, method="words", token_length=100)
            for chunk in chunks:
                try:
                    chunk_no = i
                    i += 1
                    collection.data.insert(
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
