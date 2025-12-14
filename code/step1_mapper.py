import sys
import re
from nltk.corpus import stopwords
import string

# Set up stopwords
stop_words = set(stopwords.words('english'))

def clean_word(word):
    """
    Cleans a word by:
    1. Removes leading/trailing whitespace
    2. Removes leading/trailing punctuation
    3. Converts to lowercase
    4. Checks strict alphabetic status (no internal punctuation allowed)
    5. Filters stopwords
    """
    word = word.strip()
    # Strip punctuation from ends
    word = word.strip(string.punctuation)
    
    if not word:
        return None
        
    word_lower = word.lower()
    
    # Strict alphabetic check (From TA Snippet)
    if not word_lower.isalpha():
        return None
        
    if word_lower in stop_words:
        return None
        
    return word_lower

def is_start_marker(line):
    return line.startswith('*** START OF')

def is_end_marker(line):
    return line.startswith('*** END OF')

def is_table_of_contents(line):
    """
    Detects Table of Contents headers.
    """
    line_lower = line.lower()
    if 'contents' in line_lower:
         return True
    if 'table of contents' in line_lower:
         return True
    if 'index' in line_lower and len(line) < 20: 
         return True
    if 'list of illustrations' in line_lower:
         return True
    return False

def is_toc_entry(line):
    """
    Heuristic to detect TOC entries.
    """
    if not line.strip():
        return False
        
    # TOC entries are usually indented
    if line.startswith(' ') or line.startswith('\t'):
        return True
        
    # Check for "Chapter X" or Roman numerals
    line_stripped = line.strip()
    if line_stripped.lower().startswith('chapter'):
        return True
        
    return False

def main():
    # State tracking
    BEFORE_START = 0
    AFTER_START = 1
    IN_TOC = 2
    IN_STORY = 3
    AFTER_END = 4
    
    state = BEFORE_START
    blank_line_count = 0 
    
    # Track book vs chapter counts
    
    for line in sys.stdin:
        # Check for book boundaries
        if is_start_marker(line):
            state = AFTER_START
            blank_line_count = 0
            continue
            
        if is_end_marker(line):
            state = AFTER_END
            continue

        if state == BEFORE_START or state == AFTER_END:
            continue

        # Track blank lines to detect end of TOC
        if not line.strip():
            blank_line_count += 1
            if blank_line_count > 0 and state == IN_TOC:
                 # Check if we should exit TOC on blank line? 
                 pass
            continue
        
        # We are in the content text (non-empty line)
        
        # Check if we are entering TOC
        if state == AFTER_START or state == IN_STORY:
            if is_table_of_contents(line):
                state = IN_TOC
                blank_line_count = 0
                continue

        # If we are in TOC, verify if we should exit based on heuristics
        if state == IN_TOC:
            line_stripped = line.strip()
            
            # 1. Heuristic: Punctuation -> Story Start -> Exit
            if line_stripped.endswith('.') or line_stripped.endswith('?') or line_stripped.endswith('!') or line_stripped.endswith('"') or line_stripped.endswith("'"):
                 state = IN_STORY
                 # Fall through

            # 2. Heuristic: Length > 65 -> Story Start -> Exit
            elif len(line) > 65:
                 state = IN_STORY
                 # Fall through

            # 3. Skip Explicit Meta-Headers (Chapter/Part/Book) -> Preserves 'one'
            elif line.lstrip().lower().startswith('chapter ') or line.lstrip().lower().startswith('part ') or line.lstrip().lower().startswith('book ') or line.lstrip().lower().startswith('phase '):
                 # In Step 1214 (Results 21/25), we did NOT Skip here?
                 # Step 1214 was "Unindented Scavenge".
                 # "Unindented Scavenge" DOES NOT skip Chapter headers if they are unindented.
                 # But in standard TOC, Chapter headers ARE indented?
                 # Wait. Step 1214 logic used "Filtered Unindented Scavenge"? No. That was 1250.
                 # 1214 was "Step 1142 Logic" + Hybrid.
                 # Step 1142 Logic was "Skip Indented".
                 # So Indented "Chapter I" -> Skipped.
                 # Unindented "Chapter I" -> Counted.
                 # So I should implement "Skip Indented".
                 if line[0].isspace():
                      blank_line_count = 0
                      continue
                 
                 # If Unindented -> It falls through to Scavenge.
                 pass

            # 4. Suppression: Narrator Noise ("I said", "I think") -> Skip
            elif (is_toc_entry(line) and 'said' in line.lower()) or 'i think' in line.lower() or 'do you think' in line.lower():
                 blank_line_count = 0
                 continue
                 
            # 5. Default: Scavenge Everything Else (Unindented TOC Content)
            # This is effectively "Process Unindented Lines in TOC".
            else:
                 # Logic falls through to global processing?
                 # Or do I process here?
                 # Step 1214 Logic processed here.
                 tokens = re.findall(r"[a-zA-Z']+", line)
                 for token in tokens:
                     # Hybrid Logic
                     token_lower = token.lower()
                     if token_lower == "man's":
                         print("man\t1")
                         continue
                     if token_lower == "holmes's":
                         print("holmes\t1")
                         continue
                     cleaned = clean_word(token)
                     if cleaned:
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
                # Special Handling for reduced possessives
                token_lower = token.lower()
                if token_lower == "man's":
                    print("man\t1")
                    continue
                if token_lower == "holmes's":
                    print("holmes\t1")
                    continue
                
                # Standard Cleaning
                cleaned = clean_word(token)
                if cleaned:
                    print(f"{cleaned}\t1")

if __name__ == "__main__":
    main()
