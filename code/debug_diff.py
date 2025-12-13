
import re
import sys

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

def matches_explicit_skip(line):
    line_lower = line.lstrip().lower()
    return (line_lower.startswith('chapter ') or 
            line_lower.startswith('part ') or 
            line_lower.startswith('book ') or 
            line_lower.startswith('phase '))

with open('results/combined_input.txt', 'r') as f:
    for line in f:
        line = line.strip()
        if not line: continue
        
        # Check for 'said'
        if 'said' not in line.lower():
            continue
            
        # Check if 776 Skipped it (Matches TOC)
        if is_toc_entry(line):
            # Check if 832 Counts it
            if not matches_explicit_skip(line):
                # 832 Logic: Punct OR Length -> Exit.
                is_punct = (line.endswith('.') or line.endswith('?') or line.endswith('!') or line.endswith('"') or line.endswith("'"))
                is_long = (len(line) > 65)
                
                # We want lines that are LONG but NOT Punct.
                # (If Punct, 776 would have Exited too).
                # (If Short, 832 would have Default Skipped).
                if is_long and not is_punct:
                    print(f"FOUND CULPRIT: {line}")
                    print(f"Length: {len(line)}")
