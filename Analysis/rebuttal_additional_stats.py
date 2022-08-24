"""
Script to compute the following additional statistics for the rebuttal:
  - Distribution of Celex IDs across languages (i.e., in how many languages is the sample present)

"""
import pickle
from collections import Counter


def get_language_availability_distribution(data):

    # Iterate through all samples to find out how many times a particular celex id occurs across languages.
    # We don't need to iterate through validation and test, since those samples are available in all languages.
    for lang, all_data in data.items():
        for split, samples in all_data.items():
            if split != "train":
                continue

            for celex_id, _ in samples.items():
                train_celex_occurrences.append(celex_id)

    train_celex_occurrences = Counter(train_celex_occurrences)
    print(f"Length of validation set: {len(data['english']['validation'])}")
    print(f"Length of test set: {len(data['english']['test'])}")


    # We only care about the number of languages an article is in, not the ID
    grouped_by_frequency = Counter(train_celex_occurrences.values())
    # And then sort for better legibility
    by_frequency_tuples = sorted(list(grouped_by_frequency.items()), key=lambda row: row[0])
    for how_many_langs, count in by_frequency_tuples:
        print(f"{count} samples are available in exactly {how_many_langs} languages.")

    more_than_20 = sum([grouped_by_frequency[how_many_langs] for how_many_langs in range(20, 24)])
    # 375 is the total number of validation + test samples
    print(f"{(more_than_20 + 375) / (len(train_celex_occurrences) + 375) * 100:.2f}% of samples are available in "
          f"20 or more languages.")

    less_than_10 = sum([grouped_by_frequency[how_many_langs] for how_many_langs in range(1, 11)])
    print(f"{(less_than_10) / (len(train_celex_occurrences) + 375) * 100:.2f}% of samples are available in "
          f"less than 10 languages.")


if __name__ == '__main__':
    total_count = 0
    train_celex_occurrences = []

    with open("clean_data.pkl", "rb") as f:
        data = pickle.load(f)

    get_language_availability_distribution(data)

    del data
