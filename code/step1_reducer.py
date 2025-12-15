import sys

def main():
    """
    Reducer: Aggregates word counts from sorted mapper output.
    Expects input to be sorted by word.
    Keeps only one word's count in memory at a time.
    Then sorts by frequency and outputs results.
    """
    
    word_counts = {}
    current_word = None
    current_count = 0
    
    # Phase 1: Stream through input and aggregate counts
    for line in sys.stdin:
        line = line.strip()
        
        if not line:
            continue
        
        # Parse the mapper output: word\t1
        try:
            word, count = line.split('\t')
            count = int(count)
        except ValueError:
            # Skip malformed lines
            continue
        
        # If we encounter a new word, save the previous word's count
        if word != current_word:
            if current_word is not None:
                word_counts[current_word] = current_count
            
            # Start counting the new word
            current_word = word
            current_count = count
        else:
            # Same word, accumulate count
            current_count += count
    
    # Don't forget to save the last word
    if current_word is not None:
        word_counts[current_word] = current_count
    
    # Phase 2: Sort by count (descending), then alphabetically for tie-breaking
    sorted_words = sorted(word_counts.items(), key=lambda x: (-x[1], x[0]))
    
    # Phase 3: Output sorted results
    for word, count in sorted_words:
        print(f"{word}\t{count}")

if __name__ == "__main__":
    main()