import sys
import re
from nltk.corpus import stopwords

# Load English stopwords from NLTK
STOP_WORDS = set(stopwords.words('english'))

# State machine for parsing Project Gutenberg books
# States: BEFORE_START, AFTER_START, IN_TOC, IN_STORY, AFTER_END
BEFORE_START = 0
AFTER_START = 1
IN_TOC = 2
IN_STORY = 3
AFTER_END = 4

state = BEFORE_START
blank_line_count = 0

for line in sys.stdin:
    line = line.rstrip()
    
    # Track blank lines to help detect TOC end
    if not line.strip():
        blank_line_count += 1
        continue
    else:
        # Reset blank line counter when we see content
        had_blank_lines = blank_line_count > 0
        blank_line_count = 0
    
    # State transitions
    if '*** START OF' in line:
        state = AFTER_START
        continue
    
    if '*** END OF' in line:
        state = AFTER_END
        continue
    
    # Detect TOC start (only if we're in AFTER_START state)
    if state == AFTER_START and re.search(r'^(TABLE OF )?CONTENTS?$', line.strip(), re.IGNORECASE):
        state = IN_TOC
        continue
    
    # Handle TOC: skip only actual TOC chapter listings
    if state == IN_TOC:
        stripped = line.strip()
        
        # TOC entries are characterized by leading whitespace (indentation)
        # Exit TOC when we see a non-empty line without leading whitespace
        
        if len(stripped) == 0:
            # Empty line in TOC, skip it
            continue
        elif line.startswith(' ') or line.startswith('\t'):
            # Indented line = TOC entry, skip it
            continue
        else:
            # Non-empty, non-indented line = end of TOC, start of story
            state = IN_STORY
            # Don't continue - process this line as story content
    
    # Process content only in AFTER_START and IN_STORY states
    if state == AFTER_START or state == IN_STORY:
        # Extract words from lines
        words = re.findall(r'\b[\w\']+\b', line)
        
        for word in words:
            # Clean word: remove punctuation, lowercase
            word = word.lower()
            word = re.sub(r'[^a-z]', '', word)
            
            # Filter: minimum length 3, alphabetic only, not a stop word
            if len(word) >= 3 and word.isalpha() and word not in STOP_WORDS:
                print(f"{word}\t1")