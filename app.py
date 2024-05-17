import streamlit as st
import utils
from config import wiki_collection_name


# @app.route("/llm-or-rag")
# def compare_llm_rag():
#     user_prompt = request.args.get("prompt")
#     collection_name = request.args.get("collection")
#     llm_response = utils.ask_llm(user_prompt)
#     rag_response = utils.ask_rag(user_prompt, collection_name)

#     return {"llm response": llm_response, "rag response": rag_response}


# @app.route("/search")
# def search():
#     user_query = request.args.get("query")
#     collection_name = request.args.get("collection")
#     search_responses = utils.search(user_query, collection_name)

#     return search_responses

client = utils.get_weaviate_client()

search_responses = utils.search_comparison(
    client=client,
    collection_name=wiki_collection_name,
    user_query="sports"
)

for index, response in search_responses.items():
    st.write(f"Index: {index}")
    st.write(response[1])
