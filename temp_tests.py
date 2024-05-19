import utils
import config
from weaviate.classes.query import Filter

# print(utils.ask_llm("What is the capital of France?"))
# print(utils.ask_llm("What is multi-tenancy?", provider="ollama"))
# print(utils.ask_llm("What is the capital of France?", search_queries_only=True))

client = utils.get_weaviate_client()


# print(utils.search(client=client, collection_name=config.wiki_collection_name, user_query="sports", target_vector="default"))
# print(utils.ask_rag(client=client, collection_name=config.etienne_collection_name, user_prompt="what is multi-tenancy?", target_vector=config.etienne_index_name))
# print(utils.video_rag(client=client, collection_name=config.etienne_collection_name, search_query="multi-tenancy?", prompt="what is multi-tenancy?"))
# print(utils.ask_etienne(client=client, user_question="what is multi-tenancy?"))

coll = client.collections.get(config.knowledge_base_name)

response = coll.query.hybrid(
    query="JP Hwang bio",
    limit=5,
    target_vector=config.chunks_index_name,
    filters=Filter.by_property("title").equal("JP"),
)

for o in response.objects:
    print(o.properties["title"])
    print(o.properties["chunk"][:100])


client.close()
