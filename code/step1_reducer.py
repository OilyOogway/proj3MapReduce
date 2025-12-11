import sys

word_counts = {}

for line in sys.stdin:
    line = line.strip()
    
    # Skip empty lines
    if not line:
        continue
    
    # Parse input: word\tcount
    try:
        word, count = line.split('\t')
        count = int(count)
    except ValueError:
        # Skip malformed lines
        continue
    
    # Aggregate counts
    if word in word_counts:
        word_counts[word] += count
    else:
        word_counts[word] = count

# Sort by count (descending) and output
sorted_words = sorted(word_counts.items(), key=lambda x: (-x[1], x[0]))

# Print result
for word, count in sorted_words:
    print(f"{word} {count}")