from flask import Flask, request, render_template, session, redirect, url_for
from werkzeug.utils import secure_filename
from SpeechServices import SpeechServices
from Logger import *
from datetime import datetime

import os
import dotenv
import requests


# Start log config
Logger.setup_logging()
dotenv.load_dotenv()
''' 
Get response from chatbot API 
param: model_name - name of the model
param: user_input - user input(question)
return: chatbot_respone - response from chatbot API as string
'''
def get_response_from_chatbot_api(model_name, user_input)->str:
    url = f"http://{os.getenv('CONTAINER_B')}:{os.getenv('FLASK_API_PORT')}/chat"
    headers = {'content-type': 'application/json'}
    data = {'model_name': model_name, 'user_input': user_input}
    response = requests.post(url, json=data, headers=headers)
    if response.ok:
        chatbot_respone = response.json()['response']
        return chatbot_respone
    else:
        logging.error("Error communicating with chatbot API. Please try again.")
        return "Error communicating with chatbot API. Please try again."


''' Send request API to create schema in Weaviate '''
def send_request_to_create_schema():
    url = f"http://{os.getenv('CONTAINER_B')}:{os.getenv('FLASK_API_PORT')}/create_weaviate_schema"
    ''' Due to depends on problem, we need to retry the request until the server is up and running.'''
    while True:
        try:
            response = requests.post(url)
            break
        except requests.exceptions.ConnectionError:
            continue
        except Exception as e:
            logging.error(f"Error creating Weaviate schema: {e}")
            break
    
    logging.info(response.json()['message'])


''' Get all data in POST request and store as dict'''
def get_files_from_UI(request):
    request_files = {}
    request_files['user_input'] = request.form.get('user_input', '')
    request_files['audio_file'] = request.files['audio_file']
    request_files['model_selected'] = request.form.get('model', 'microsoft/DialoGPT-medium')
    return request_files


''' Create Flask app '''
def create_app():
    app = Flask(__name__, static_folder='/app/static')
    app.secret_key = os.getenv('FLASK_SECRET_KEY')
    app.config['UPLOAD_FOLDER'] = os.getenv('AUDIO_MEDIA_DIR')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    ''' Send request API to create schema in Weaviate '''
    send_request_to_create_schema()

    @app.route('/', methods=['GET', 'POST'])
    def home():
        if 'chats' not in session:
            session['chats'] = []
        if 'current_chat' not in session:
            session['current_chat'] = []

        if request.method == 'POST':
            ''' Get all data in POST request and store as dict'''
            request_files = get_files_from_UI(request)
            if request_files['user_input']:
                ''' Get response from chatbot API'''
                response = get_response_from_chatbot_api(request_files['model_selected'], request_files['user_input'])
                audio_file_name = f'output_{datetime.now().strftime("%Y%m%d%H%M%S")}.wav'
                audio_output_file = SpeechServices.synthesize_text(response, os.path.join(app.config['UPLOAD_FOLDER'], audio_file_name))
                session['current_chat'].append({'user_input': request_files['user_input'], 'response': response, 'audio_output_file': audio_file_name, 'model': request_files['model_selected']})
            elif 'audio_file' in request.files:
                audio_file = request_files['audio_file']
                user_input = SpeechServices.transcribe_audio_blob(audio_file)
                response = get_response_from_chatbot_api(request_files['model_selected'], user_input)
                session['current_chat'].append({'user_input': user_input, 'response': response, 'audio_output_file': audio_output_file, 'model': request_files['model_selected']})

            session.modified = True

        return render_template('index.html', current_chat=session['current_chat'], chats=session['chats'])
    
    @app.route('/new_chat', methods=['GET'])
    def new_chat():
        if 'current_chat' in session and session['current_chat']:
            session['chats'].append(session['current_chat'])
            session['current_chat'] = []
            session.modified = True
        return redirect(url_for('home'))
    
    ''' View chat history in basic UI '''
    @app.route('/view_chat/<int:chat_index>', methods=['GET'])
    def view_chat(chat_index):
        if 'chats' in session and chat_index < len(session['chats']):
            requested_chat = session['chats'][chat_index]
            return render_template('view_chat.html', chat=requested_chat, chat_index=chat_index)
        return redirect(url_for('home'))

    ''' Clear session '''
    @app.route('/clear-session', methods=['POST'])
    def clear_session():
        session.pop('current_chat', None) 
        session.pop('chats', None)
        return redirect(url_for('home'))

    
    ''' View chat history with table '''
    @app.route('/database', methods=['GET'])
    def database():
        url = f'{os.getenv("WEAVIATE_CLIENT_URL")}:{os.getenv("WEAVIATE_CLIENT_PORT")}/v1/objects?class={os.getenv("SCHEMA_NAME")}'
        response = requests.get(url)
        data = response.json()
        return render_template('database.html', data=data['objects'])
  
    return app
