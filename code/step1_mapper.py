import re
import sys
import string
from typing import Optional

from nltk.corpus import stopwords

# Load NLTK stop words once.
STOP_WORDS = set(stopwords.words('english'))

# Patterns that mark Gutenberg metadata boundaries.
START_MARKER_PATTERNS = [
    r'\*\*\* START OF',
    r'\*\*\*START OF',
]

END_MARKER_PATTERNS = [
    r'\*\*\* END OF',
    r'\*\*\*END OF',
]

# Patterns used to detect table-of-contents sections.
TOC_HEADER_PATTERNS = [
    r'^contents?:?$',
    r'^table of contents:?$',
]

TOC_ENTRY_PATTERNS = [
    r'^[ivxlc]+\.?\s',
    r'^\d+\.?\s',
    r'^chapter\s+[ivxlc\d]+',
    r'^part\s+[ivxlc\d]+',
    r'^prologue',
    r'^epilogue',
    r'^appendix',
    r'^preface',
    r'^introduction',
]

def is_metadata_line(line: str) -> bool:
    stripped = line.strip()
    return (
        stripped.startswith('Book:') or
        stripped.startswith('Author:') or
        stripped.startswith('Year:')
    )

def is_start_marker(line: str) -> bool:
    return any(re.search(pattern, line, re.IGNORECASE) for pattern in START_MARKER_PATTERNS)


def is_end_marker(line: str) -> bool:
    return any(re.search(pattern, line, re.IGNORECASE) for pattern in END_MARKER_PATTERNS)


def is_table_of_contents(line: str) -> bool:
    normalized = line.lower().strip()
    return any(re.match(pattern, normalized, re.IGNORECASE) for pattern in TOC_HEADER_PATTERNS)


def is_toc_entry(line: str) -> bool:
    normalized = line.strip().lower()
    return any(re.match(pattern, normalized) for pattern in TOC_ENTRY_PATTERNS)


def clean_word(word: str) -> Optional[str]:
    """
    Normalize a token and filter out noise words based on TA guidance.
    """
    word = word.strip(string.punctuation + '""''—–')
    word = word.lower()

    if len(word) < 3:
        return None

    if word in STOP_WORDS:
        return None

    if not word.isalpha():
        return None

    return word

def should_skip_separator(line: str) -> bool:
    return line.strip().startswith('=====')

def process_stdin():
    """
    Replicate the TA's text-cleaning pipeline before emitting mapper output.
    """
    text = sys.stdin.read()
    # Join hyphenated words broken across lines.
    text = re.sub(r'([A-Za-z])-\r?\n([A-Za-z])', r'\1\2', text)

    in_content = True
    saw_markers = False
    skipping_toc = False

    for line in text.splitlines():
        if is_start_marker(line):
            saw_markers = True
            in_content = True
            skipping_toc = False
            continue

        if is_end_marker(line):
            if saw_markers:
                in_content = False
            skipping_toc = False
            continue

        if not in_content:
            continue

        if should_skip_separator(line):
            continue

        stripped = line.strip()
        if not stripped:
            continue

        if is_metadata_line(stripped):
            continue

        if is_table_of_contents(stripped):
            skipping_toc = True
            continue

        if skipping_toc and is_toc_entry(stripped):
            continue
        
        tokens = re.findall(r"\b[\w']+\b", line)
        for token in tokens:
            cleaned = clean_word(token)
            if cleaned:
                print(f"{cleaned}\t1")


if __name__ == "__main__":
    process_stdin()
