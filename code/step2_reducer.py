import sys
from collections import defaultdict
from typing import Dict, DefaultDict

def process_reducer():
    """
    Reducer: aggregate counts of words per year from mapper output.
    Input format: word \t year \t count
    Output: prints total counts per word and per year in sorted order.
    """
    # Nested dictionary: word -> year -> count
    aggregate_counts: DefaultDict[str, DefaultDict[int, int]] = defaultdict(lambda: defaultdict(int))

    current_word: str = ""
    current_year: int = 0
    current_count: int = 0

    for raw_line in sys.stdin:
        raw_line = raw_line.strip()
        if not raw_line:
            continue

        # Split line into word, year, count
        parts = raw_line.split('\t')
        if len(parts) != 3:
            continue  # Skip malformed lines

        word, year_str, count_str = parts
        try:
            year = int(year_str)
            count = int(count_str)
        except ValueError:
            continue  # Skip lines with invalid integers

        # Aggregate counts for consecutive keys
        if word == current_word and year == current_year:
            current_count += count
        else:
            if current_word:
                aggregate_counts[current_word][current_year] += current_count
            current_word = word
            current_year = year
            current_count = count

    # Add last accumulated count
    if current_word:
        aggregate_counts[current_word][current_year] += current_count

    # Output sorted results
    for word in sorted(aggregate_counts.keys()):
        year_counts: Dict[int, int] = aggregate_counts[word]
        total_count = sum(year_counts.values())
        print(f"Word: {word} (Total: {total_count})")
        for year in sorted(year_counts.keys()):
            count = year_counts[year]
            print(f"  {year}: {count:5d}")

if __name__ == "__main__":
    process_reducer()
