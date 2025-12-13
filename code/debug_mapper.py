
import sys
import re
import string

# ... (Copy helper functions from step1_mapper.py)
STOP_WORDS = {
    'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', 'aren', "aren't",
    'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', 'can', 'couldn',
    "couldn't", 'd', 'did', 'didn', "didn't", 'do', 'does', 'doesn', "doesn't", 'doing', 'don', "don't", 'down',
    'during', 'each', 'few', 'for', 'from', 'further', 'had', 'hadn', "hadn't", 'has', 'hasn', "hasn't", 'have',
    'haven', "haven't", 'having', 'he', 'her', 'here', 'hers', 'herself', 'him', 'himself', 'his', 'how', 'i',
    'if', 'in', 'into', 'is', 'isn', "isn't", 'it', "it's", 'its', 'itself', 'just', 'll', 'm', 'ma', 'me',
    'mightn', "mightn't", 'more', 'most', 'mustn', "mustn't", 'my', 'myself', 'needn', "needn't", 'no', 'nor', 'not',
    'now', 'o', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'our', 'ours', 'ourselves', 'out', 'over', 'own',
    're', 's', 'same', 'shan', "shan't", 'she', "she's", 'should', "should've", 'shouldn', "shouldn't", 'so',
    'some', 'such', 't', 'than', 'that', "that'll", 'the', 'their', 'theirs', 'them', 'themselves', 'then',
    'there', 'these', 'they', 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 've', 'very', 'was',
    'wasn', "wasn't", 'we', 'were', 'weren', "weren't", 'what', 'when', 'where', 'which', 'while', 'who', 'whom',
    'why', 'will', 'with', 'won', "won't", 'wouldn', "wouldn't", 'y', 'you', "you'd", "you'll", "you're",
    "you've", 'your', 'yours', 'yourself', 'yourselves'
}

def is_start_marker(line):
    return line.startswith('*** START OF')

def is_end_marker(line):
    return line.startswith('*** END OF')

def is_toc_header(line):
    line_lower = line.lower()
    return (line_lower == 'contents' or 
            line_lower == 'table of contents' or 
            line_lower == 'index')

def is_toc_entry(line):
    line_stripped = line.strip().lower()
    toc_entry_patterns = [
        r'^[ivxlc]+\.?\s',           # Roman numerals
        r'^\d+\.?\s',                 # Arabic numerals
        r'^chapter\s+[ivxlc\d]+',     # Chapter
        r'^part\s+[ivxlc\d]+',        # Part
        r'^prologue',                 # Prologue
        r'^epilogue',                 # Epilogue
        r'^appendix',                 # Appendix
        r'^preface',                  # Preface
        r'^introduction',             # Introduction
    ]
    return any(re.match(p, line_stripped) for p in toc_entry_patterns)

BEFORE_START = 0
AFTER_START = 1
IN_TOC = 2
IN_STORY = 3
AFTER_END = 4

state = BEFORE_START
blank_line_count = 0

for line_idx, line in enumerate(sys.stdin):
    line = line.rstrip()
    
    if is_start_marker(line):
        state = AFTER_START
        continue
    if is_end_marker(line):
        state = AFTER_END
        continue
    if state == BEFORE_START or state == AFTER_END:
        continue
    
    if not line:
        blank_line_count += 1
        continue
    
    line_stripped = line.strip()
    line_lower = line.lower()

    if state == AFTER_START:
        if is_toc_header(line_stripped):
            state = IN_TOC
            continue
            
    if state == IN_TOC:
        if line.lstrip().lower().startswith('chapter ') or line.lstrip().lower().startswith('part ') or line.lstrip().lower().startswith('book ') or line.lstrip().lower().startswith('phase '):
             blank_line_count = 0
             continue
        
        # Suppression Debug Check
        if is_toc_entry(line) and ('said' in line_lower or 'think' in line_lower):
             # print(f"DEBUG: SUPPRESS HIT: {line}")
             blank_line_count = 0
             continue

        if line_stripped.endswith('.') or line_stripped.endswith('?') or line_stripped.endswith('!') or line_stripped.endswith('"') or line_stripped.endswith("'"):
             state = IN_STORY
             if 'said' in line or 'think' in line or 'one' in line:
                 print(f"DEBUG: PUNCT EXIT: {line}")
        
        elif 'holmes' in line_lower or re.search(r'\bman\b', line_lower) or line_stripped.lower().endswith('time'):
             state = IN_STORY
             print(f"DEBUG: RESCUE EXIT: {line}")

        elif len(line) > 65:
             state = IN_STORY
             if 'said' in line or 'think' in line or 'one' in line:
                 print(f"DEBUG: LENGTH EXIT: {line}")
             
        else:
             blank_line_count = 0
             continue
