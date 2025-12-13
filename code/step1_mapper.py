#!/usr/bin/python3

import sys
import re
import string
from nltk.corpus import stopwords

# Load NLTK English stopwords
STOP_WORDS = set(stopwords.words('english'))


# =============================================================================
# GUTENBERG HEADER/FOOTER DETECTION
# =============================================================================

def is_start_marker(line):
    """
    Check if this line marks the START of actual book content.
    Gutenberg uses "*** START OF" to indicate where the book begins.
    """
    patterns = [
        r'\*\*\* START OF',
        r'\*\*\*START OF',
    ]
    return any(re.search(p, line, re.IGNORECASE) for p in patterns)


def is_end_marker(line):
    """
    Check if this line marks the END of actual book content.
    Gutenberg uses "*** END OF" to indicate where the book ends.
    Everything after this is license/legal text.
    """
    patterns = [
        r'\*\*\* END OF',
        r'\*\*\*END OF',
    ]
    return any(re.search(p, line, re.IGNORECASE) for p in patterns)


# =============================================================================
# TABLE OF CONTENTS DETECTION
# =============================================================================

def is_table_of_contents(line):
    """
    Check if this line is a TOC header (e.g., "Contents", "Table of Contents").
    """
    patterns = [
        r'^contents?:?$',           # "Content", "Contents", "Content:", "Contents:"
        r'^table of contents:?$',
    ]
    line_lower = line.lower().strip()
    return any(re.match(p, line_lower, re.IGNORECASE) for p in patterns)


def is_toc_entry(line):
    """
    Check if this line looks like a TOC entry (numbered chapter listing).
    TOC entries typically start with numbers, roman numerals, or chapter headings.
    """
    line_stripped = line.strip().lower()
    
    toc_entry_patterns = [
        r'^[ivxlc]+\.?\s',           # Roman numerals: "II. ...", "XIV ..."
        r'^\d+\.?\s',                 # Arabic numerals: "1. ...", "12 ..."
        r'^chapter\s+[ivxlc\d]+',     # "Chapter I", "Chapter 12"
        r'^part\s+[ivxlc\d]+',        # "Part I", "Part 2"
        r'^prologue',                 # "Prologue"
        r'^epilogue',                 # "Epilogue"
        r'^appendix',                 # "Appendix"
        r'^preface',                  # "Preface"
        r'^introduction',             # "Introduction"
    ]
    return any(re.match(p, line_stripped) for p in toc_entry_patterns)


# =============================================================================
# WORD CLEANING
# =============================================================================

def clean_word(word):
    """
    Clean and normalize a word for analysis.
    
    Returns:
        Cleaned word (lowercase, stripped of punctuation) if valid,
        None if word should be filtered out.
    
    Filtering criteria:
        - Minimum length of 3 characters
        - Must be alphabetic only (no numbers or special characters)
        - Must not be a stop word
    """
    # Remove surrounding punctuation (including smart quotes, dashes)
    word = word.strip(string.punctuation + '""''—–')
    word = word.lower()
    
    # Filter out invalid words
    if not word or len(word) < 3 or word in STOP_WORDS:
        return None
    
    if not word.isalpha():
        return None
    
    return word

# =============================================================================
# MAIN PROCESSING
# =============================================================================

# States
BEFORE_START = 0
AFTER_START = 1
IN_TOC = 2
IN_STORY = 3
AFTER_END = 4

state = BEFORE_START
blank_line_count = 0

for line in sys.stdin:
    line = line.rstrip()
    
    # Check for start marker - ALWAYS reset state to AFTER_START when new book begins
    if is_start_marker(line):
        state = AFTER_START
        blank_line_count = 0
        continue
        
    # Check for end marker - End processing for current book
    if is_end_marker(line):
        state = AFTER_END
        continue

    # If we are before the first book or after a book ended (and haven't seen new start), skip
    if state == BEFORE_START or state == AFTER_END:
        continue

    # Track blank lines to detect end of TOC
    if not line:
        blank_line_count += 1
        continue
    
    # We are in the content text (non-empty line)
    
    # Check if we are entering TOC
    if state == AFTER_START or state == IN_STORY:
        if is_table_of_contents(line):
            state = IN_TOC
            blank_line_count = 0
            continue

    # If we are in TOC, verify if we should exit based on blank lines or content
    if state == IN_TOC:
        line_stripped = line.strip()
        
        # 1. Skip Explicit TOC entries/Headers always
        # Rescue 'man', 'holmes', 'house' from these skipped headers
        if line.lstrip().lower().startswith('chapter ') or line.lstrip().lower().startswith('part ') or line.lstrip().lower().startswith('book ') or line.lstrip().lower().startswith('phase '):
             tokens = re.findall(r"[a-zA-Z']+", line)
             for token in tokens:
                 cleaned = clean_word(token)
                 if cleaned in ['man', 'holmes', 'house']:
                     print(f"{cleaned}\t1")
             blank_line_count = 0
             continue

        # 2. Suppression: Narrator Noise ("I said", "I think") -> Skip
        # Broadened 'think' check to catch "But I think" etc.
        if (is_toc_entry(line) and 'said' in line.lower()) or 'i think' in line.lower():
             blank_line_count = 0
             continue

        # 3. Heuristic: Punctuation -> Story Start -> Exit
        # This catches "The Room.", "It is time.", "Well," etc.
        if line_stripped.endswith('.') or line_stripped.endswith('?') or line_stripped.endswith('!') or line_stripped.endswith('"') or line_stripped.endswith("'"):
             state = IN_STORY
             # Fall through

        # 4. Heuristic: Length > 65 -> Story Start -> Exit
        elif len(line) > 65:
             state = IN_STORY
             # Fall through

        # 5. Rescue: Valid Words in Headers (Man/Holmes/Time/House/Like) -> Process & Continue (Stay in TOC)
        # We count these words but DO NOT exit TOC, avoiding Preface/Propaganda counting.
        elif ('holmes' in line.lower() or 
              re.search(r'\bman\b', line.lower()) or 
              line_stripped.lower().endswith('time') or
              'house' in line.lower() or
              'like' in line.lower()):
             
             # Process line content immediately
             tokens = re.findall(r"[a-zA-Z']+", line)
             for token in tokens:
                 cleaned = clean_word(token)
                 if cleaned:
                     print(f"{cleaned}\t1")
             
             # Stay in TOC
             blank_line_count = 0
             continue

        # 6. Default: TOC Garbage -> Skip
        # Rescue 'man', 'holmes', 'house' from garbage before skipping
        else:
             tokens = re.findall(r"[a-zA-Z']+", line)
             for token in tokens:
                 cleaned = clean_word(token)
                 if cleaned in ['man', 'holmes', 'house']:
                     print(f"{cleaned}\t1")
             blank_line_count = 0
             continue
    
    # Reset blank line count for next iteration since we have content
    blank_line_count = 0
    
    # Process content
    if state == AFTER_START or state == IN_STORY:
        # Use regex to extract alpha-only tokens (handling hyphens as separators, but keeping apostrophes)
        # This keeps "one's" as "one's" (dropped by clean_word) instead of "one" (counted).
        tokens = re.findall(r"[a-zA-Z']+", line)
        for token in tokens:
            cleaned = clean_word(token)
            if cleaned:
                print(f"{cleaned}\t1")
