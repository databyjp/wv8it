from weaviate.classes.config import Configure, Property, DataType, Multi2VecField
from weaviate.util import generate_uuid5
from tqdm import tqdm
import utils
from config import multimodal_name, default_generative_config
import pandas as pd
import requests
from datetime import datetime, timezone
import json
import zipfile
from pathlib import Path
import base64

client = utils.get_weaviate_client()

coll_name = multimodal_name

utils.safe_delete_collection(client, coll_name)

if not client.collections.exists(coll_name):
    client.collections.create(
        name=coll_name,
        properties=[
            Property(name="title", data_type=DataType.TEXT),
            Property(name="overview", data_type=DataType.TEXT),
            Property(name="vote_average", data_type=DataType.NUMBER),
            Property(name="genre_ids", data_type=DataType.INT_ARRAY),
            Property(name="release_date", data_type=DataType.DATE),
            Property(name="tmdb_id", data_type=DataType.INT),
            Property(name="poster", data_type=DataType.BLOB),
        ],
        # Define & configure the vectorizer module
        vectorizer_config=[
            Configure.NamedVectors.multi2vec_clip(
                name="default",
                image_fields=[
                    Multi2VecField(name="poster", weight=0.9)
                ],  # 90% of the vector is from the poster
                text_fields=[
                    Multi2VecField(name="title", weight=0.1)
                ],  # 10% of the vector is from the title
            ),
        ],
        # Define the generative module
        generative_config=default_generative_config
    )

mm_coll = client.collections.get(coll_name)


data_url = "https://raw.githubusercontent.com/weaviate-tutorials/edu-datasets/main/movies_data_1990_2024.json"
resp = requests.get(data_url)
df = pd.DataFrame(resp.json())

# Create a directory for the images
img_dir = Path("data/posters")
img_dir.mkdir(parents=True, exist_ok=True)

# Download images
posters_url = "https://raw.githubusercontent.com/weaviate-tutorials/edu-datasets/main/movies_data_1990_2024_posters.zip"
posters_path = img_dir / "movies_data_1990_2024_posters.zip"
posters_path.write_bytes(requests.get(posters_url).content)

# Unzip the images
with zipfile.ZipFile(posters_path, "r") as zip_ref:
    zip_ref.extractall(img_dir)

# Get the collection
mm_coll = client.collections.get(multimodal_name)

# Enter context manager
with mm_coll.batch.fixed_size(50) as batch:
    # Loop through the data
    for i, movie in tqdm(df.iterrows()):
        # Convert data types
        # Convert a JSON date to `datetime` and add time zone information
        release_date = datetime.strptime(movie["release_date"], "%Y-%m-%d").replace(
            tzinfo=timezone.utc
        )
        # Convert a JSON array to a list of integers
        genre_ids = json.loads(movie["genre_ids"])
        # Convert image to base64
        img_path = img_dir / f"{movie['id']}_poster.jpg"
        with open(img_path, "rb") as file:
            poster_b64 = base64.b64encode(file.read()).decode("utf-8")

        # Build the object payload
        movie_obj = {
            "title": movie["title"],
            "overview": movie["overview"],
            "vote_average": movie["vote_average"],
            "genre_ids": genre_ids,
            "release_date": release_date,
            "tmdb_id": movie["id"],
            "poster": poster_b64,
        }

        # Add object to batch queue
        batch.add_object(
            properties=movie_obj,
            uuid=generate_uuid5(movie["id"])
            # references=reference_obj  # You can add references here
        )
        # Batcher automatically sends batches

# Check for failed objects
if len(mm_coll.batch.failed_objects) > 0:
    print(f"Failed to import {len(mm_coll.batch.failed_objects)} objects")
    for failed in mm_coll.batch.failed_objects:
        print(f"e.g. Failed to import object with error: {failed.message}")

client.close()
