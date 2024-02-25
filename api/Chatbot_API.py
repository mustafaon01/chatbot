from flask import Flask, request, jsonify
from chatbot import Chatbot
from Logger import *
import dotenv

# Start log config
Logger.setup_logging()
dotenv.load_dotenv()

def create_app():
    app = Flask(__name__)

    @app.route('/chat', methods=['POST'])
    def chat():
        model_name = request.json['model_name']
        user_input = request.json['user_input']
        chatbot = Chatbot(model_name=model_name)
        response = chatbot.chat(user_input)
        return jsonify({'response': response})
    
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
