import utils
from weaviate.classes.config import Property, DataType, Configure
from weaviate.util import generate_uuid5
from dotenv import load_dotenv
import os
from pathlib import Path
from tqdm import tqdm
from embedkit import EmbedKit
from embedkit.classes import Model

load_dotenv()

client = utils.get_weaviate_client()

collection_name = "SlideDeck"

utils.safe_delete_collection(client, collection_name)

pdf_collection = client.collections.create(
    name=collection_name,
    properties=[
        Property(name="filepath", data_type=DataType.TEXT),
        Property(name="image", data_type=DataType.BLOB),
        Property(name="page", data_type=DataType.INT),
    ],
    vectorizer_config=[
        Configure.NamedVectors.none(
            name="cohere",
            vector_index_config=Configure.VectorIndex.hnsw(
                quantizer=Configure.VectorIndex.Quantizer.sq()
            )
        ),
    ],
)

pdf_dir = Path("./data/slides")
pdf_files = sorted(list(pdf_dir.glob("*.pdf")))

kit = EmbedKit.cohere(
    api_key=os.getenv("COHERE_API_KEY"),
    model=Model.Cohere.EMBED_V4_0,
    image_batch_size=8
)

with pdf_collection.batch.fixed_size(10) as batch:
    for pdf_file in pdf_files:
        print(f"Processing {pdf_file.name}")
        results = kit.embed_pdf(pdf_file)

        for i, obj in tqdm(enumerate(results.objects)):
            batch.add_object(
                properties={
                    "filepath": pdf_file.name,
                    "image": obj.source_b64,
                    "page": i + 1,
                },
                vector={
                    "cohere": obj.embedding,
                },
                uuid=generate_uuid5(f"{collection_name};{pdf_file.name};{i+1}"),
            )

if pdf_collection.batch.failed_objects:
    print(pdf_collection.batch.failed_objects[0].message)

print(len(pdf_collection))

client.close()
