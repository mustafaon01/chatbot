from Logger import *
from transformers import AutoTokenizer, AutoModelForCausalLM
from sentence_transformers import SentenceTransformer
from weaviate import Client

import json
import warnings
import dotenv
import os


# Start log config
Logger.setup_logging()
dotenv.load_dotenv()
warnings.filterwarnings(action='ignore', category=ResourceWarning)

weaviate_client = Client(url=f"{os.getenv('WEAVIATE_CLIENT_URL')}:{os.getenv('WEAVIATE_CLIENT_PORT')}",
                         additional_headers={'X-HuggingFace-Api-Key': os.getenv('X_HUGGINGFACE_API_KEY')})

class Chatbot:
    def __init__(self, model_name="microsoft/DialoGPT-medium"):
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
        self.sentence_model = f"sentence-transformers/{os.getenv('SENTENCE_TRANSFORMER_MODEL_NAME')}"
        self.sentence_transformer = SentenceTransformer(self.sentence_model)
        self.schema_name = os.getenv('SCHEMA_NAME')
    
    def create_weaviate_schema(self):
        schema = {
        "classes": [
          {
            "class": self.schema_name,
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
            ]
          }
        ]
      }
        if weaviate_client.schema.exists(self.schema_name):
            logging.info("Schema already exists.")
        else:
            weaviate_client.schema.create(schema)
            logging.info("Schema created.")
    
    def json_print(self, data):
        print(json.dumps(data, indent=2))
    
    def laod_to_weaviate(self, question, answer):
        if question is not None and answer is not None:
          
          object_to_store = {
                  "question": question,
                  "answer": answer
                  }
          
          weaviate_client.data_object.create(data_object=object_to_store, class_name=self.schema_name)
          logging.info("Loaded to Weaviate successfully.")
        else:
            logging.info("Question and answer is None.")

    def generate_response_from_model(self, question):
        try:
          input_ids = self.tokenizer.encode(question + self.tokenizer.eos_token, return_tensors='pt')

          pad_token_id = self.tokenizer.eos_token_id if self.tokenizer.eos_token_id is not None else None

          chat_history_ids = self.model.generate(
              input_ids,
              max_length=100,
              pad_token_id=pad_token_id
          )

          response = self.tokenizer.decode(chat_history_ids[:, input_ids.shape[-1]:][0], skip_special_tokens=True)

          return response
        except Exception as e:
            logging.error(f"Error during the generating response: {e}")
            return "Sorry, I encountered an error while generating a response."

    def get_similar_questions_from_weaviate(self, question):
        question_embedding = self.sentence_transformer.encode(question, convert_to_tensor=True).tolist()
        # semantic search
        search_results = weaviate_client.query.get(self.schema_name, ["question", "answer", "_additional {id, certainty}"]).with_near_vector(
            {"vector": question_embedding}).with_limit(5).do()

        results = search_results['data']['Get'][self.schema_name]

        filtered_results = [
            result for result in results
            if result['_additional']['certainty'] >= 0.95
        ]
        logging.info(f"filtered_results: {filtered_results}")

        if filtered_results:
            logging.info("Found similar question in Weaviate.")
            result = filtered_results[0]
            logging.info(f"result: {result}")
            return result
        else:
            return None
    
    def chat(self, question):
        similar_question = self.get_similar_questions_from_weaviate(question)
        if similar_question:
            logging.info(f"Found similar interaction: {similar_question['question']} - {similar_question['answer']}")
            answer = similar_question['answer']
        else:
            logging.info("No similar interaction found. Generating a new response.")
            answer = self.generate_response_from_model(question)
        
        self.laod_to_weaviate(question, answer)
        return answer
     