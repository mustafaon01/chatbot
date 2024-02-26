from textblob import TextBlob
import re


''' FILTER METHODS TO AVOID MISS INPUT VALUES '''

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
