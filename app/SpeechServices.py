from google.cloud import speech, texttospeech
from dotenv import load_dotenv
from Logger import *

import os


# Start log config
Logger.setup_logging()
load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")


class SpeechServices:
    """
    Provides methods for STT and TTS
    """

    @staticmethod
    def transcribe_audio(audio_file_path):
        """
        Transcribes the audio from a file path to text.

        :param audio_file_path: The path to the audio file to be transcribed.
        :return: A string containing the transcribed text.
        """
        client = speech.SpeechClient()

        with open(audio_file_path, "rb") as audio_file:
            content = audio_file.read()

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
            logging.error(f"Error transcribing audio: {e}")
            return None

        transcripts = [result.alternatives[0].transcript for result in response.results]
        return ' '.join(transcripts)

    @staticmethod
    def transcribe_audio_blob(audio_content):
        """
        Transcribes audio content directly from binary data to text.

        :param audio_content: The binary audio content to be transcribed.
        :return: A string containing the transcribed text.
        """
        client = speech.SpeechClient()

        audio = speech.RecognitionAudio(content=audio_content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            language_code="en-US"
        )

        response = client.recognize(config=config, audio=audio)
        transcripts = [result.alternatives[0].transcript for result in response.results]

        return ' '.join(transcripts)

    @staticmethod
    def synthesize_text(text, output_file_path):
        """
        Synthesizes speech from the provided text and saves it to a file.

        :param text: The text to be synthesized into speech.
        :param output_file_path: The file path where the synthesized audio should be saved.
        :return: The path to the output audio file, or None if an error occurred.
        """
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
            logging.error(f"Error synthesizing speech: {e}")
            return None

        with open(output_file_path, "wb") as output_audio_file:
            output_audio_file.write(response.audio_content)

        logging.info(f"Synthesized audio saved to: {output_file_path}")
        return output_file_path
