from weaviate.classes.config import Configure
from typing import List
from distyll.config import COLLECTION_NAME

ETIENNE_VIDEOS = [
    "https://youtu.be/K1R7oK2piUM",  # Our Mad Journey of Building a Vector Database in Go - Weaviate at FOSDEM 2023
    "https://youtu.be/4sLJapXEPd4",  # Weaviate: An Architectural Deep Dive (Etienne Dilocker)
    "https://youtu.be/KT2RFMTJKGs",  # Etienne AI conference talk on multi-tenancy
    "https://youtu.be/0diVrgyQwXA",  # Etienne Brown University talk on Quantization
    "https://youtu.be/IesakuRUrLE",  # Etienne and Instabase Shipping Trustworthy AI Products
]

DSPY_VIDEOS = [
    "https://youtu.be/41EfOY0Ldkc",  # DSPy Explained!
    "https://youtu.be/ickqCzFxWj0",  # DSPy + Weaviate for the Next Generation of LLM Apps
    "https://youtu.be/CEuUG4Umfxs",  # Getting Started with RAG in DSPy!
]

etienne_collection_name = "EtienneTextChunk"
wiki_name = "WikiChunk"
knowledge_base_name = COLLECTION_NAME
multimodal_name = "Multimodal"
chunks_index_name = "chunk"

MAX_N_CHUNKS = 8

generative_config_llama3 = Configure.Generative.ollama(
    model="llama3",
    api_endpoint="http://host.docker.internal:11434",
)
generative_config_phi3 = Configure.Generative.ollama(
    model="phi3:mini",
    api_endpoint="http://host.docker.internal:11434",
)
generative_config_openai = Configure.Generative.openai(
    model="gpt-3.5-turbo",
)
generative_config_command_r_plus = Configure.Generative.cohere(model="command-r-plus")
generative_config_command_r = Configure.Generative.cohere(model="command-r")

default_generative_config = generative_config_command_r


def vectorizer_config_ollama(
    vector_name: str,
    source_properties: List[str],
    model: str = "snowflake-arctic-embed",
):
    return Configure.NamedVectors.text2vec_ollama(
        name=vector_name,
        source_properties=source_properties,
        model=model,
        api_endpoint="http://host.docker.internal:11434",
        vector_index_config=Configure.VectorIndex.hnsw(
            quantizer=Configure.VectorIndex.Quantizer.bq()
        ),
    )


def vectorizer_config_cohere(
    vector_name: str,
    source_properties: List[str],
    model: str = "embed-multilingual-v3.0",
):
    return Configure.NamedVectors.text2vec_cohere(
        name=vector_name,
        source_properties=source_properties,
        model=model,
        vector_index_config=Configure.VectorIndex.hnsw(
            quantizer=Configure.VectorIndex.Quantizer.bq()
        ),
    )
