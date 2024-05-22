## WV8it - A Weaviate demo app

Weaviate is an AI-native vector database. This demo app showcases various capabilities that can be achieved with Weaviate.

### Overview

This app uses a combination of Weaviate, Streamlit and Ollama, as well as the Cohere API. Note that Ollama and the Cohere API can be replaced with other services that provide similar functionality.

If you are using the Cohere API, you will need to sign up for an account and get an API key. Then, save it as an environment variable with the name `COHERE_APIKEY`.

### Setup

1. Clone this repository
1. (Optional) Activate a virtual environment
1. Run Weaviate with: `docker compose up`
1. Install the dependencies with `pip install -r requirements.txt`
1. Run the app with `streamlit run 1_$'\360\237\247\240'_Mind_reading.py`  (Or `streamlit run 1_🧠_Mind_reading.py`)
