from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from chatbot import Chatbot
import os
import dotenv
from werkzeug.utils import secure_filename
from stt import transcribe_audio, synthesize_text
import uuid
from textblob import TextBlob
import re

dotenv.load_dotenv()

class SpellingCorrector:
    @staticmethod
    def correct_spelling(text):
        corrected_text = TextBlob(text).correct()
        return str(corrected_text)

class InputNormalizer:
    @staticmethod
    def normalize_input(text):
        text = text.lower().strip()
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s]', '', text)
        return text

class InputLimiter:
    @staticmethod
    def limit_input_length(text, max_length=280):
        return text[:max_length]

class SecurityChecker:
    @staticmethod
    def sanitize_input(text):
        #XSS
        sanitized_text = re.sub(r'<[^>]*?>', '', text)
        return sanitized_text


def create_app():
  app = Flask(__name__)
  # app.secret_key = os.getenv('FLASK_SECRET_KEY')
  app.secret_key = 'Ju3S3dwqYr3ds?dm'
  app.config['UPLOAD_FOLDER'] = 'static/uploads'
  chatbot = Chatbot()
  chatbot.create_weaviate_schema()

  @app.route('/', methods=['GET', 'POST'])
  def hello():
      if 'chats' not in session:
          session['chats'] = []
      if 'current_chat' not in session:
          session['current_chat'] = []

      if request.method == 'POST':
          user_input = request.form.get('user_input', '')
          audio_file = request.files['audio_file']
          model_selected = request.form.get('model', 'defaultModel')
          selected_chatbot = Chatbot(model_name=model_selected)
          if user_input:
              response = selected_chatbot.chat(user_input)
              audio_output_file = synthesize_text(response, os.path.join(app.config['UPLOAD_FOLDER'], f'output_{uuid.uuid4()}.wav'))
              session['current_chat'].append({'user_input': user_input, 'response': response, 'audio_output_file': audio_output_file, 'model': model_selected})
          elif audio_file and audio_file.filename != '':
              filename = secure_filename(audio_file.filename)
              file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
              audio_file.save(file_path)
              try:
                  print("file_path: ", file_path)
                  user_input = transcribe_audio(file_path)
                  print("user_input: ", user_input)
                  # response = f"Audio processed, transcription: {user_input}"
                  response = selected_chatbot.chat(user_input)
                  audio_output_file = synthesize_text(response, os.path.join(app.config['UPLOAD_FOLDER'], f'output_{uuid.uuid4()}.wav')) 
              except Exception as e:
                  response = "Error processing audio"
                  print(f"Error transcribing audio: {e}")
              finally:
                  print("finally")
                  #os.remove(file_path)
              
              session['current_chat'].append({'user_input': user_input, 'response': response, 'audio_output_file': audio_output_file, 'model': model_selected})

          session.modified = True

      return render_template('index.html', current_chat=session['current_chat'], chats=session['chats'])
  @app.route('/new_chat', methods=['GET'])
  def new_chat():
      if 'current_chat' in session and session['current_chat']:
          session['chats'].append(session['current_chat'])
          session['current_chat'] = []
          session.modified = True
      return redirect(url_for('hello'))
  
  @app.route('/view_chat/<int:chat_index>', methods=['GET'])
  def view_chat(chat_index):
    if 'chats' in session and chat_index < len(session['chats']):
        requested_chat = session['chats'][chat_index]
        return render_template('view_chat.html', chat=requested_chat, chat_index=chat_index)
    return redirect(url_for('hello'))
  
  return app

'''if __name__ == '__main__':
  app = create_app()
  app.run(debug=True, host="0.0.0.0", port=8000)'''