import utils
import config

# print(utils.ask_llm("What is the capital of France?"))
print(utils.ask_llm("What is multi-tenancy?", provider="ollama"))
# print(utils.ask_llm("What is the capital of France?", search_queries_only=True))

# client = utils.get_weaviate_client()

# print(utils.search(client=client, collection_name=config.wiki_collection_name, user_query="sports", target_vector="default"))
# print(utils.ask_rag(client=client, collection_name=config.etienne_collection_name, user_prompt="what is multi-tenancy?", target_vector=config.etienne_index_name))
# print(utils.video_rag(client=client, collection_name=config.etienne_collection_name, search_query="multi-tenancy?", prompt="what is multi-tenancy?"))
# print(utils.ask_etienne(client=client, user_question="what is multi-tenancy?"))
