import string
from typing import List

import nltk
from nltk.tokenize import sent_tokenize, word_tokenize

nltk.download("punkt", quiet=True)


def tokenize_sentences(text: str) -> List[str]:
    return sent_tokenize(text)


def tokenize_words(text: str) -> List[str]:
    return [word for word in word_tokenize(text) if word not in string.punctuation]
