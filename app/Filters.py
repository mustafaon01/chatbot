from textblob import TextBlob
from profanity_check import predict, predict_prob
import re


''' Correct spelling of input text '''
class SpellingCorrector:
    @staticmethod
    def correct_spelling(text):
        corrected_text = TextBlob(text).correct()
        return str(corrected_text)


''' Delete extra spacese from input text '''
class InputNormalizer:
    @staticmethod
    def normalize_input(text):
        text = text.lower().strip()
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s]', '', text)
        return text


''' Limit the length of input text '''
class InputLimiter:
    @staticmethod
    def limit_input_length(text, max_length=280):
        return text[:max_length]


''' Profanity checker'''
class ProfanityChecker:
    ''' If return 1, the text is profane. If return 0, the text is not profane.'''
    @staticmethod
    def check_profanity(text):
        return predict([text])[0]

    @staticmethod
    def check_profanity_prob(text):
        return predict_prob([text])[0]
