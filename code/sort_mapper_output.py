#!/usr/bin/env python3
"""
Sort mapper output by word (first column) for MapReduce reducer.
This ensures all instances of the same word are grouped together.

Usage:
    type mapper_output.txt | python sort_mapper_output.py > sorted_output.txt
    cat mapper_output.txt | python sort_mapper_output.py > sorted_output.txt
"""

import sys

def main():
    # Read all lines from stdin
    lines = []
    for line in sys.stdin:
        line = line.strip()
        if line:
            lines.append(line)
    
    # Sort by the word (everything before the tab)
    # This ensures all "word\t1" entries are grouped together
    lines.sort(key=lambda x: x.split('\t')[0] if '\t' in x else x)
    
    # Output sorted lines
    for line in lines:
        print(line)

if __name__ == "__main__":
    main()