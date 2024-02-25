from transformers import AutoTokenizer, AutoModelForCausalLM
from sentence_transformers import SentenceTransformer
from weaviate import Client
import json
import warnings
import torch
import dotenv
import os

dotenv.load_dotenv()
warnings.filterwarnings(action='ignore', category=ResourceWarning)

schema_name = os.getenv('SCHEMA_NAME')
model_name = "microsoft/DialoGPT-medium"
model_name3 = "gpt2-medium"
model_name4 = "EleutherAI/gpt-neo-1.3B"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

weaviate_client = Client(url=f"{os.getenv('WEAVIATE_CLIENT_URL')}:{os.getenv('WEAVIATE_CLIENT_PORT')}", 
                         additional_headers={'X-HuggingFace-Api-Key': os.getenv('X_HUGGINGFACE_API_KEY')})



sentence_model = f"sentence-transformers/{os.getenv('SENTENCE_TRANSFORMER_MODEL_NAME')}"
print(f"sentence_model: {sentence_model}")
sentence_transformer = SentenceTransformer(sentence_model)

def create_weaviate_schema():
    schema = {
        "classes": [
          {
            "class": schema_name,
            "vectorizer": "text2vec-huggingface",
            "vectorIndexConfig": {
             "distance": "cosine",
            },
            "moduleConfig": {
            "generative-cohere": {}
            },
            "description": "Stores chat history between user and bot along with embeddings.",
            "properties": [
              {
                "name": "question",
                "dataType": ["text"],
                "description": "The user's question or input."
              },
              {
                "name": "answer",
                "dataType": ["text"],
                "description": "The bot's response."
              }
              ,
              {
                "name": "embeddings",
                "dataType": ["vector"],
                "description": "Embeddings for the chat interaction."
              }
            ]
          }
        ]
      }
    if weaviate_client.schema.exists(schema_name):
        print("Schema_name: ", schema_name)
        print("Schema already exists.")
    else:
        weaviate_client.schema.create(schema)
        print("Schema created successfully.")

def jprint(data):
    print(json.dumps(data, indent=2))

def store_chat_interaction_in_weaviate1(question, answer):
    if question is not None and answer is not None:
        # chat_text = f"{question} {answer}"
        
        chat_embedding = sentence_transformer.encode(answer, convert_to_tensor=True)
        
        object_to_store = {
            "class": schema_name,
            "properties": {
                "question": question,
                "answer": answer
                }
            }
        
        weaviate_client.data_object.create(data_object=object_to_store, class_name=schema_name)
        print("Chat interaction stored in Weaviate.")
    else:
        print("Question or answer is None. Not storing in Weaviate.")

def store_chat_interaction_in_weaviate(question, answer):
    if question is not None and answer is not None:
        
        object_to_store = {
                "question": question,
                "answer": answer
                }
        
        weaviate_client.data_object.create(data_object=object_to_store, class_name=schema_name)
        print("Chat interaction stored in Weaviate.")
    else:
        print("Question or answer is None. Not storing in Weaviate.")

def get_similar_questions_from_weaviate1(question):
    question_embedding = sentence_transformer.encode(question, convert_to_tensor=True).tolist()
    # semantic search
    search_results = weaviate_client.query.get(schema_name, ["question", "answer", "_additional {id, certainty}"]).with_near_vector({"vector": question_embedding}).with_limit(1).do()
    print(f"search_results: {search_results}")
    if search_results['data']['Get'][schema_name]:
        print("Found similar question in Weaviate.")
        result = search_results['data']['Get'][schema_name][0]
        print(f"result: {result}")
        return result
    else:
        return None

def get_similar_questions_from_weaviate(question):
    question_embedding = sentence_transformer.encode(question, convert_to_tensor=True).tolist()
    # semantic search
    search_results = weaviate_client.query.get(schema_name, ["question", "answer", "_additional {id, certainty}"]).with_near_vector({"vector": question_embedding}).with_limit(5).do()

    # search_results içindeki verilere doğru şekilde erişim
    results = search_results['data']['Get'][schema_name]

    filtered_results = [
        result for result in results
        if result['_additional']['certainty'] >= 0.95
    ]
    print(f"filtered_results: {filtered_results}")

    if filtered_results:
        print("Found similar question in Weaviate.")
        result = filtered_results[0]  # İlk uygun sonucu al
        print(f"result: {result}")
        return result
    else:
        return None


def generate_response1(question):
    input_ids = tokenizer.encode(question + tokenizer.eos_token, return_tensors='pt')

    chat_history_ids = model.generate(input_ids, max_length=1000, pad_token_id=tokenizer.eos_token_id)

    response = tokenizer.decode(chat_history_ids[:, input_ids.shape[-1]:][0], skip_special_tokens=True)

    return response

def generate_response(question):
    try:
        input_ids = tokenizer.encode(question + tokenizer.eos_token, return_tensors='pt')

        pad_token_id = tokenizer.eos_token_id if tokenizer.eos_token_id is not None else None

        chat_history_ids = model.generate(
            input_ids,
            max_length=100,
            pad_token_id=pad_token_id
        )

        response = tokenizer.decode(chat_history_ids[:, input_ids.shape[-1]:][0], skip_special_tokens=True)

        return response
    except Exception as e:
        print(f"Error in generate_response: {e}")
        return "Sorry, I encountered an error while generating a response."

def chat_with_bot(question):
    
    similar_interaction = get_similar_questions_from_weaviate(question)
    
    if similar_interaction:
        print(f"Found similar interaction: {similar_interaction['question']} - {similar_interaction['answer']}")
        answer = similar_interaction['answer']
    else:
        print("No similar interaction found. Generating a new response.")
        answer = generate_response(question)

    store_chat_interaction_in_weaviate(question, answer)

    return answer


#create_weaviate_schema()
#jprint(weaviate_client.schema.get("ChatHistory2"))

if __name__ == "__main__":
    create_weaviate_schema()
    i = 0
    while i <10:
        question = input("you: ")
        print(chat_with_bot(question))
        i += 1
