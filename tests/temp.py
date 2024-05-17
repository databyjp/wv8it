import requests


for question in ["How does multi-tenancy work?", "What is the capital of France?"]:
    response = requests.get(
        "http://127.0.0.1:5000/ask-etienne", params={"question": question}
    )

    print(question)
    print(response.status_code)
    print(response.text)


for question in ["How does multi-tenancy work?", "What is the capital of France?"]:
    response = requests.get(
        "http://127.0.0.1:5000/llm-or-rag",
        params={"prompt": "What is the capital of France?"},
    )

    print(question)
    print(response.status_code)
    print(response.text)
