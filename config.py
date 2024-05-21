from distyll.config import CHUNK_COLLECTION
from weaviate.classes.config import Configure

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
knowledge_base_name = CHUNK_COLLECTION
multimodal_name = "Multimodal"
chunks_index_name = "chunk"

MAX_N_CHUNKS = 8

# generative_config = Configure.Generative.ollama(
#     model="llama3",
#     api_endpoint="http://host.docker.internal:11434",
# )
# generative_config = Configure.Generative.openai(
#     model="gpt-4",
# )
generative_config = Configure.Generative.cohere(model="command-r-plus")
