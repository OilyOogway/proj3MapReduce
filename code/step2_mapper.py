import sys
import re
import os
import string
from typing import Optional, Set

from nltk.corpus import stopwords

# Load English stop words once
STOP_WORDS = set(stopwords.words('english'))
#expect to run code from root directory
TOP_WORDS_PATH = "step1_topwords.txt"

def is_separator(line: str) -> bool:
    return line.strip().startswith('=' * 5)

def load_top_words() -> Set[str]:
    """
    Load the list of top words from the file specified in the environment variable.
    """
    top_words_path = TOP_WORDS_PATH
    if not top_words_path:
        sys.stderr.write("Error: TOP_WORDS_FILE environment variable not set\n")
        sys.exit(1)

    top_words_set = set()
    with open(top_words_path, 'r') as f:
        for raw_line in f:
            raw_line = raw_line.strip()
            if not raw_line:
                continue
            word = raw_line.split('\t')[0]
            top_words_set.add(word)
    return top_words_set

def normalize_word(token: str) -> Optional[str]:
    """
    Normalize and filter a token: lowercase, remove punctuation, skip stop words, skip short or non-alpha.
    """
    token = token.strip(string.punctuation + '""''—–')
    token = token.lower()
    if not token or len(token) < 3 or token in STOP_WORDS:
        return None
    if not token.isalpha():
        return None
    return token

def process_input():
    """
    Main mapper loop: read stdin, extract and emit valid words for top words with year.
    """
    top_words = load_top_words()
    in_metadata_section = False
    year_value: Optional[int] = None

    for raw_line in sys.stdin:
        raw_line = raw_line.rstrip()

        # Toggle metadata flag for separator lines
        if is_separator(raw_line):
            in_metadata_section = not in_metadata_section
            continue

        # Extract year from metadata section
        if in_metadata_section:
            stripped_line = raw_line.strip()
            if stripped_line.startswith('Year:'):
                year_text = stripped_line.split(':', 1)[1].strip()
                year_value = int(year_text)
            continue

        # Skip lines until year is known
        if year_value is None:
            continue

        # Skip empty lines
        if not raw_line.strip():
            continue

        # Tokenize line into words
        tokens = re.findall(r"\b[\w']+\b", raw_line)
        for token in tokens:
            cleaned = normalize_word(token)
            if cleaned and cleaned in top_words:
                print(f"{cleaned}\t{year_value}\t1")

if __name__ == "__main__":
    process_input()
