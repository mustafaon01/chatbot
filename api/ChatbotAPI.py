from flask import Flask, request, jsonify
from Transformers import Chatbot
from Logger import *

import dotenv

# Start log config
Logger.setup_logging()
dotenv.load_dotenv()

''' Create Flask API to respond to chat requests '''
def create_app():
    app = Flask(__name__)

    ''' Endpoint to chat with chatbot '''
    @app.route('/chat', methods=['POST'])
    def chat():
        model_name = request.json['model_name']
        user_input = request.json['user_input']
        chatbot = Chatbot(model_name=model_name)
        response = chatbot.chat(user_input)
        return jsonify({'response': response})
    
    ''' Endpoint to create Weaviate schema '''
    @app.route('/create_weaviate_schema', methods=['POST'])
    def create_weaviate_schema():
        chatbot = Chatbot()
        try:
            chatbot.create_weaviate_schema()
            return jsonify({'message': 'Weaviate schema created successfully using API.'}), 201
        except Exception as e:
            logging.error(f"Error creating Weaviate schema in API: {e}")
            return jsonify({'message': 'Error creating Weaviate schema using API.'}), 500
        
    return app
