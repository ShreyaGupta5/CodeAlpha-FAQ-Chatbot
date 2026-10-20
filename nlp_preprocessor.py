"""
NLP Preprocessor Module
Handles text cleaning, tokenization, stop-word removal, and lemmatization using NLTK.
"""

import re
import string
from typing import List

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# Ensure required NLTK resources are available silently
def ensure_nltk_resources():
    resources = ['punkt', 'punkt_tab', 'stopwords', 'wordnet', 'omw-1.4']
    for resource in resources:
        try:
            nltk.data.find(f'tokenizers/{resource}' if 'punkt' in resource else f'corpora/{resource}')
        except (LookupError, FileNotFoundError):
            try:
                nltk.download(resource, quiet=True)
            except Exception:
                pass

ensure_nltk_resources()


class TextPreprocessor:
    """
    Cleans and pre-processes raw user text and FAQ corpus using NLTK:
    - Lowercasing
    - Noise & punctuation removal
    - Tokenization
    - Stopwords removal
    - WordNet Lemmatization
    """

    def __init__(self, remove_stopwords: bool = True):
        self.lemmatizer = WordNetLemmatizer()
        self.remove_stopwords = remove_stopwords
        
        # Load English stopwords
        try:
            self.stop_words = set(stopwords.words('english'))
        except Exception:
            self.stop_words = {
                'a', 'an', 'the', 'is', 'are', 'was', 'were', 'in', 'on', 'at', 
                'to', 'for', 'of', 'with', 'by', 'about', 'and', 'or', 'so',
                'what', 'how', 'when', 'where', 'why', 'who', 'which', 'can'
            }

    def clean_text(self, text: str) -> str:
        """
        Cleans the string by lowercasing and stripping special characters.
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Lowercase
        text = text.lower().strip()
        
        # Remove URLs and email addresses
        text = re.sub(r'https?://\S+|www\.\S+', '', text)
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove non-alphanumeric characters (keep basic spaces)
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def tokenize(self, text: str) -> List[str]:
        """
        Tokenizes text into individual words using NLTK word_tokenize with regex fallback.
        """
        cleaned = self.clean_text(text)
        if not cleaned:
            return []
            
        try:
            tokens = word_tokenize(cleaned)
        except Exception:
            # Fallback regex tokenizer if NLTK punkt is unavailable
            tokens = re.findall(r'\b\w+\b', cleaned)
            
        return tokens

    def lemmatize_token(self, token: str) -> str:
        """
        Lemmatizes a single token across noun and verb forms.
        """
        # Lemmatize as noun first, then verb
        lemma = self.lemmatizer.lemmatize(token, pos='n')
        lemma = self.lemmatizer.lemmatize(lemma, pos='v')
        return lemma

    def preprocess(self, text: str) -> str:
        """
        Complete preprocessing pipeline:
        Cleaning -> Tokenizing -> Stopword Filtering -> Lemmatization -> Joined String.
        If all words are stopwords (e.g. 'who are you'), retains lemmatized tokens.
        """
        tokens = self.tokenize(text)
        if not tokens:
            return ""
            
        # Try filtering stopwords
        filtered_tokens = []
        for token in tokens:
            if self.remove_stopwords and token in self.stop_words:
                continue
            token_lemma = self.lemmatize_token(token)
            if len(token_lemma) > 1 or token_lemma in {'a', 'i'}:
                filtered_tokens.append(token_lemma)
                
        # If empty (e.g. "who are you"), preserve all lemmatized tokens
        if not filtered_tokens:
            for token in tokens:
                token_lemma = self.lemmatize_token(token)
                if len(token_lemma) > 1 or token_lemma in {'a', 'i'}:
                    filtered_tokens.append(token_lemma)
                
        return " ".join(filtered_tokens)


# Global preprocessor instance for convenience
default_preprocessor = TextPreprocessor()

def preprocess_text(text: str) -> str:
    """Convenience helper to preprocess text with default settings."""
    return default_preprocessor.preprocess(text)


if __name__ == "__main__":
    sample = "How can I track my shipped orders and packages?"
    print(f"Original: {sample}")
    print(f"Cleaned & Lemmatized: {preprocess_text(sample)}")
