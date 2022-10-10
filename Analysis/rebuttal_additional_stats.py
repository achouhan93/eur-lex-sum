"""
Script to compute the following additional statistics for the rebuttal:
  - Distribution of Celex IDs across languages (i.e., in how many languages is the sample present).
  - N-gram novelty across subsets, particularly for documents with multiple references.

"""
import json
import pickle
from collections import Counter

from compute_final_offline_stats import get_novel_ngrams


def get_language_availability_distribution(data):

    train_celex_occurrences = []

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


def get_ngram_novelty_for_subsets(data):
    # Load the additional data with the subset info
    with open("./Insights/single_reference_subset.json") as f:
        single_reference_celex_ids = json.load(f)
    with open("./Insights/multiple_reference_subset.json") as f:
        multi_reference_celex_ids = json.load(f)
    with open("./Insights/multiple_reference_texts.json") as f:
        multi_reference_texts = json.load(f)

    all_english_samples = {}
    for _, samples in data["english"].items():
        all_english_samples.update(samples)

    print("N-gram novelty ratios for the full English set (train + val + test combined)")
    print(f"Verify length of full combined English data: {len(all_english_samples)}")
    print_ngram_stats(all_english_samples)

    print("N-gram novelty ratios for the single reference subset")
    single_reference_subset = {}
    for celex_id in single_reference_celex_ids:
        try:
            single_reference_subset[celex_id] = all_english_samples[celex_id]
        # Some ids might have been filtered out in between these steps.
        except KeyError:
            continue
    print(f"Verify length of single reference subset: {len(single_reference_subset)}")
    print_ngram_stats(single_reference_subset)

    print("N-gram novelty ratios for the multi reference subset with single document texts")
    multi_reference_subset = {}
    for celex_id in multi_reference_celex_ids:
        try:
            multi_reference_subset[celex_id] = all_english_samples[celex_id]
        # Some ids might have been filtered out in between these steps.
        except KeyError:
            continue
    print(f"Verify length of multi reference subset: {len(multi_reference_subset)}")
    print_ngram_stats(multi_reference_subset)

    print("N-gram novelty ratios for the multi reference subset with all referenced document texts concatenated")
    multi_reference_subset_long_texts = {}
    for celex_id in multi_reference_celex_ids:
        try:
            multi_reference_subset_long_texts[celex_id] = {"reference_text": multi_reference_texts[celex_id],
                                                           "summary_text": all_english_samples[celex_id]["summary_text"]}
        # Some ids might have been filtered out in between these steps.
        except KeyError:
            continue
    print(f"Verify length of multi reference subset (concatenated): {len(multi_reference_subset_long_texts)}")
    print_ngram_stats(multi_reference_subset_long_texts)


def print_ngram_stats(subset):
    novel_ratio_for_language = get_novel_ngrams(subset, max_ngram_length=4)
    ratio_string = f"Novel n-gram ratios: "
    for ratio in novel_ratio_for_language:
        ratio_string += f"& {ratio * 100:.2f} "
    ratio_string += "\\\\"
    print(ratio_string)


if __name__ == '__main__':

    with open("clean_data.pkl", "rb") as f:
        data = pickle.load(f)

    get_language_availability_distribution(data)

    get_ngram_novelty_for_subsets(data)

    # Enable this to avoid pycharm or other interactive shells from crashing after execution
    del data
