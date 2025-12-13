
import re

def is_toc_entry(line):
    line_stripped = line.strip().lower()
    toc_entry_patterns = [
        r'^[ivxlc]+\.?\s',           # Roman numerals
    ]
    print(f"Checking: '{line_stripped}'")
    for p in toc_entry_patterns:
        if re.match(p, line_stripped):
            print(f"Matched pattern: {p}")
            return True
    return False

test_line = "I laughed at this cross-examination."
print(f"Result: {is_toc_entry(test_line)}")
