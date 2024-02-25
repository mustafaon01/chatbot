from google.cloud import speech, texttospeech
import os
from dotenv import load_dotenv
from Logger import *

# Start log config
Logger.setup_logging()
load_dotenv()

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

def transcribe_audio(audio_file_path):
    client = speech.SpeechClient()

    with open(audio_file_path, "rb") as audio_file:
        content = audio_file.read()
        print("content: ", content[:10])

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code="en-US",
        model='default',
        audio_channel_count=1,
        enable_automatic_punctuation=True,
        enable_separate_recognition_per_channel=False,

    )
    try:
        response = client.recognize(config=config, audio=audio)
    except Exception as e:
        print(f"Error transcribing audio: {e}")
    print("response: ", response)
    print("response.results: ", response.results)
    transcripts = []
    for result in response.results:
        transcripts.append(result.alternatives[0].transcript)
    
    print("transcripts: ", transcripts)
    return ' '.join(transcripts)

def transcribe_audio_blob(audio_content):
    client = speech.SpeechClient()

    audio = speech.RecognitionAudio(content=audio_content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code="en-US"
    )

    response = client.recognize(config=config, audio=audio)
    transcripts = [result.alternatives[0].transcript for result in response.results]

    return ' '.join(transcripts)

def synthesize_text(text, output_file_path):
    client = texttospeech.TextToSpeechClient()

    synthesis_input = texttospeech.SynthesisInput(text=text)

    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16
    )

    try:
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
    except Exception as e:
        print(f"Error synthesizing speech: {e}")
        return None

    with open(output_file_path, "wb") as output_audio_file:
        output_audio_file.write(response.audio_content)
    logging.info(f"!!!!!!!!!{os.getcwd()}")

    logging.info(f"Synthesized audio saved to: {output_file_path}")
    return output_file_path


