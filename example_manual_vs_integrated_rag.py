# Manual RAG vs Integrated RAG

# Let's say you want to find out what some documents in particular had to say about sustainability efforts.
# Your LLM prompt might be something like:
# "Summarize the sustainability efforts of company X, Y and Z"



## Manual RAG
prompt_task = "Summarize the sustainability efforts of company X, Y and Z"
search_query = "sustainability efforts"

# Step 1: Turn query into a vector
import cohere
import os

cohere_key = os.getenv("COHERE_APIKEY")
co = cohere.Client(api_key=cohere_key)

response = co.embed(
  model='embed-multilingual-v3.0',
  texts=[search_query],
  input_type='search_document',
  embedding_types=['float'])

query_vector = response.embeddings.float[0]

# Step 2: Search for similar documents
import weaviate

client = weaviate.connect_to_local()

collection = client.collections.get("SourceText")

response = collection.query.near_vector(
    near_vector=query_vector,
    limit=10
)

results = response.objects

# Step 3: Combine the objects & query & prompt the LLM

total_text = prompt_task + "\n ===== Perform this task based on the following: =====" + "\n".join([result.properties['text'] for result in results])

response = co.chat(
  model="command-r-plus",
  message=total_text
)

print(response.text)


## Integrated RAG
import weaviate

client = weaviate.connect_to_local(
    headers={"X-Cohere-Api-Key": cohere_key}
)

collection = client.collections.get("SourceText")

response = collection.generate.near_text(
    query=search_query,
    limit=10,
    grouped_task="Summarize the sustainability efforts of company X, Y and Z"
)

print(response.generated)
