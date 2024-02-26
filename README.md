# Overview
Basic chatbot which chat with AI. AI is llm models which user can choose. Also, chat stores in vector database and each question is searched 
with vector embeddings and find most relevant old answer that model already response. This search technique is semantic search.

# Software Architecture
- There are 3 containers which are weaviate, flask-api, flask-web-server. Flask-web-server can request to weaviate-api for getting stored data. Also, it can 
request Flask-api to chat models, choose model and create Weaviate schema. All containers orchestration was done with docker-compose. Store all critical and changeable
variables in .env. 

# Used Technologies
- Weaviate vectoral database to store chat history with their vector values
- Docker & Docker-Compose
- GoogleCloudPlatform APIs (STT-TTS)
- Python
- HuggingFace transformers library
- HuggingFace sentence_transformers library
- Flask
- Recorder.js

# Why This Technologies
- Weaviate: has official image for docker, use RESTful API, connect huggingface modules with schema.
- HuggingFace repositories and transformers: Change LLM models easily, tokenizer automaticly, create vector embeddings and can semantic search.
- Flask is powerfull microservice application, I used for creating api end-points end web service. 
- Flask sessions provide a way to store information specific to a user from one request to the next.
- Recorder.js; We should use js user-client base system to get data(i.e. audio file) so, I used this js library to get audio record.

# Included LLM Models
- microsoft/DialoGPT-medium
- gpt2-medium
- EleutherAI/gpt-neo-1.3B
- If you want to add new model, you can add in index.html after line64.

# Possible Errors and Warnings
- modules timeout(waiting to restart container)
- Sometimes server get 500 beacuse of models, you can refresh the page and try again.
- STT didn't recognize the audio file
- TTS doesn't find to audio file because of flask. However, you can play tts audios in your host project path real-time.
    Also, TTS can convert error messages.
- Sometimes transformers modules timeout, we need to refresh the page.
- If change the flask port in .env file you need to change also only api(or app)/Dockerfile. [ONLY FOR FLASK PORT]
- Filtering methods are writen but not implemented in app.py because models don't work quickly and filters method make them more slower.
- You can see logs in /logs.

# Extentions
- You can listen TTS audios in app/static/uploads in this repository.
- You can also find screenshot about last audios chat history
- Flask session is basically can store chat history, also we can delete using delete button in UI.

# My Earnings
- Learn why vector database is important
- HuggingFace transformers library which called state-of-the-art
- Docker orchestration
- What is semantic search, vector embeddings
- king - man + woman ≈ queen

# Usage
```sh 
git clone https://github.com/mustafaon01/chatbot.git
```

```sh 
cd chatbot 
```

```sh 
docker-compose up --build 
```

- Open this url on your browser

```
http://localhost:8000
```

- Wait to build approximatly 6mins.
- You can change the llm model, if you change the model, then please wait download the model. (you can follow on docker-compose terminal screen)
