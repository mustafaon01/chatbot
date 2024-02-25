# chatbot

# Overview
Chatbot with changable llm models and speech-to-text, text-to-speech features. 

# Used Technologies
- Weaviate vectoral database to store chat history with their vector values
- Docker & Docker-Compose
- GoogleCloudPlatform APIs (STT-TTS)
- Python
- HuggingFace transformers library
- HuggingFace sentence_transformers library
- Flask

# Why This Technologies
- Weaviate: has official image for docker, use RESTApi, connect huggingface modules
- HuggingFace repositories and transformers: Change LLM models easily, tokenizer automaticly, create vector embeddings and can semantic search

# Possible Errors
- modules timeout(waiting to restart container)
- STT didn't recognize the audio file
- 

# Usage
``` git clone ```
``` cd chatbot ```
``` docker-compose up --build ```


