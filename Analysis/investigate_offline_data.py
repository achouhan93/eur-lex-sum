"""
Based on the (filtered) corpus of offline data, compute stats
"""

from typing import List, Dict, Tuple
import pickle
import time
import json
from collections import Counter

from tqdm import tqdm
import numpy as np

from utils import clean_text, compute_whitespace_split_length, print_language_stats, identify_document_scans, \
    identify_duplicates_by_text, identify_duplicates_by_equality, print_short_percentiles


def count_total_number_instances(samples: List[Dict]):
    occurrences = []
    for sample in samples:
        occurrences.extend(cleaned_keys(sample))

    lang_dist = Counter(occurrences)
    print(lang_dist.most_common())
    print(f"Counted {sum(dict(lang_dist.most_common()).values())} of total instances.")


def cleaned_keys(sample: Dict) -> List[str]:
    keys = list(sample.keys())
    keys.remove("celex_id")
    keys.remove("for_test_set")
    return keys


def get_lengths_and_ratios(reference_texts, summary_texts, valid_ids=None, celex_ids=None):

    if valid_ids and celex_ids:
        reference_texts = [reference_text for idx, reference_text in enumerate(reference_texts)
                           if celex_ids[idx] in valid_ids]
        summary_texts = [summary_text for idx, summary_text in enumerate(summary_texts)
                         if celex_ids[idx] in valid_ids]

    reference_token_lengths = [compute_whitespace_split_length(clean_text(text)) for text in reference_texts]
    summary_token_lengths = [compute_whitespace_split_length(clean_text(text)) for text in summary_texts]

    compression_ratios = [reference_token_lengths[i] / summary_token_lengths[i] for i in range(len(reference_texts))]

    return reference_token_lengths, summary_token_lengths, compression_ratios


def filter_duplicates(celex_ids, reference_lengths, summary_texts):
    """
    Will remove duplicates by only maintaining the *longest* reference text for one particular summary.
    """

    by_summary_lookup = {}

    for idx, (celex_id, summary_text) in enumerate(zip(celex_ids, summary_texts)):
        by_summary_lookup[summary_text] = [(celex_id, reference_lengths[idx], idx)]
        for other_idx, (other_celex_id, other_summary_text) in enumerate(zip(celex_ids, summary_texts)):
            if summary_text == other_summary_text:
                # Avoid self-hits
                if celex_id != other_celex_id:
                    by_summary_lookup[summary_text].append((other_celex_id, reference_lengths[other_idx], other_idx))

    celex_ids_to_keep = []
    for _, matched_references in by_summary_lookup.items():
        celex_ids_to_keep.append(get_longest_reference(matched_references))

    return celex_ids_to_keep


def get_longest_reference(matches):
    sort_by_length = sorted(matches, key=lambda row: row[1], reverse=True)
    select_longest_texts_celex_id = sort_by_length[0][0]
    return select_longest_texts_celex_id


def filter_short_documents(celex_ids, reference_lengths, summary_lengths, filtered_id_set) -> List[str]:

    further_filtered_id_set = []
    for celex_id, reference_length, summary_length in zip(celex_ids, reference_lengths, summary_lengths):
        # Ignore samples that have previously been dropped
        if celex_id in filtered_id_set:
            if reference_length <= summary_length:
                pass
                # sprint(f"{celex_id} has {reference_length} reference tokens, but {summary_length} summary tokens.")
            else:
                further_filtered_id_set.append(celex_id)

    return further_filtered_id_set


def get_valid_keys_for_language(samples, language) -> List[str]:
    references = []
    summaries = []
    celex_ids = []

    for sample in samples:
        if language in sample.keys():
            references.append(sample[language]["reference_text"])
            summaries.append(sample[language]["summary_text"])
            celex_ids.append(sample["celex_id"])
    reference_lengths, summary_lengths, _ = get_lengths_and_ratios(references, summaries)

    filtered_celex_ids_by_duplicates = set(filter_duplicates(celex_ids, reference_lengths, summaries))

    filtered_celex_ids = filter_short_documents(celex_ids, reference_lengths, summary_lengths,
                                                filtered_celex_ids_by_duplicates)

    print(f"{language}: {len(filtered_celex_ids)} samples after removing duplicates based on summary and length.")
    return filtered_celex_ids


def initial_analysis(samples):
    # For now only compute stats for English
    reference_texts = []
    summary_texts = []
    celex_ids = []

    for sample in samples:
        if "english" in sample.keys():
            reference_texts.append(sample["english"]["reference_text"])
            summary_texts.append(sample["english"]["summary_text"])
            celex_ids.append(sample["celex_id"])
    print("Extracted texts")
    print("Starting reference processing...")


    reference_token_lengths, summary_token_lengths, compression_ratios = get_lengths_and_ratios(reference_texts,
                                                                                                summary_texts)
    print_language_stats("English", reference_token_lengths, summary_token_lengths, compression_ratios)

    # Check documents that have an inverted compression ratio (<1.0)
    not_summary_counter = 0
    print("Documents that are not 'summaries' (i.e., summary longer than reference):")
    for idx, ratio in enumerate(compression_ratios):
        if ratio <= 1.0:
            print(celex_ids[idx])
            print(f"Length of reference text: {reference_token_lengths[idx]}")
            print(f"Length of summary text:   {summary_token_lengths[idx]}")
            not_summary_counter += 1
    print(f"{not_summary_counter} have unsuitable compression ratios")

    # Filter documents that are likely copied in their summary/reference
    equal_length = 0
    exact_match = 0
    for celex_id, ref_text, summ_text, ref_length, summ_length in zip(celex_ids, reference_texts, summary_texts,
                                                                      reference_token_lengths, summary_token_lengths):
        if ref_text == summ_text:
            print(f"{celex_id} has the exact same reference and summary")
            exact_match += 1
            equal_length += 1
        elif ref_length == summ_length:
            print(f"{celex_id} has a different text but exact same number of tokens")
            equal_length += 1

    print(f"{equal_length} documents have the same token length, {exact_match} are the exact same text.")

    identify_document_scans(celex_ids, reference_texts, summary_texts)

    # # Manually review some of the short reference texts to spot errors
    # manual_review(celex_ids, reference_texts, reference_token_lengths)

    print_short_percentiles(reference_token_lengths, summary_token_lengths)
    identify_duplicates_by_text(celex_ids, reference_texts, summary_texts,
                                reference_token_lengths, summary_token_lengths)
    identify_duplicates_by_equality(celex_ids, summary_texts, summary_token_lengths)

    # Filter ones with duplicate texts
    filtered_celex_ids = set(filter_duplicates(celex_ids, reference_token_lengths, summary_texts))
    print(f"{len(filtered_celex_ids)} after removing duplicates based on summary.")

    filtered_celex_ids = filter_short_documents(celex_ids, reference_token_lengths, summary_token_lengths,
                                                filtered_celex_ids)

    print(f"{len(filtered_celex_ids)} after further removing samples with too short references.")

    reference_token_lengths, summary_token_lengths, compression_ratios = get_lengths_and_ratios(reference_texts,
                                                                                                summary_texts,
                                                                                                filtered_celex_ids,
                                                                                                celex_ids)

    print_language_stats("English", reference_token_lengths, summary_token_lengths, compression_ratios)


def verify_samples(data: List[Dict], test_candidates: List[str], valid_ids: Dict):
    """
    Validate the data samples of validation/test set, by identifying why certain samples have been dropped from the
    complete status. This can either be an issue of length or multi-referencing.
    """
    for sample in data:
        if sample["celex_id"] not in test_candidates and sample["for_test_set"]:
            if len(sample["english"]["reference_text"]) <= len(sample["english"]["summary_text"]):
                print(f"Sample with inverse compression ratio")
            else:
                for other_sample in data:
                    try:
                        if sample["english"]["summary_text"] == other_sample["english"]["summary_text"] and \
                           sample["celex_id"] != other_sample["celex_id"]:
                            print(f"Sample with multiple document references")
                            break
                    except KeyError:
                        continue
                else:
                    for lang, ids in valid_ids.items():
                        if not sample["celex_id"] in ids:
                            print(f"{sample['celex_id']} not in {lang}")
                            for check_sample in data:
                                try:
                                    check_sample[lang]
                                except KeyError:
                                    continue
                                # identify the sample in that language
                                if check_sample["celex_id"] == sample["celex_id"]:
                                    print(f"{len(check_sample[lang]['reference_text'])} and "
                                          f"{len(check_sample[lang]['summary_text'])}")


def find_all_invalid_samples(samples: List[Dict]):
    """
    Another investigative function that prints (and stores) the celex ids with languages in which they have the same
    input and output lengths (due to a bug?).
    """
    invalid_samples = {}
    for sample in samples:
        for lang, texts in sample.items():
            if lang in {"celex_id", "for_test_set"}:
                continue

            if len(sample[lang]["reference_text"]) == len(sample[lang]["summary_text"]):
                if sample["celex_id"] not in invalid_samples.keys():
                    invalid_samples[sample["celex_id"]] = [lang]
                else:
                    invalid_samples[sample["celex_id"]].append(lang)
                print(f"{sample['celex_id']} ({lang}) with length {len(sample[lang]['reference_text'])}")


def identify_lang_ids(data: List[Dict], langs: List[str]) -> Tuple:
    """
    Will generate the list of valid Celex IDs for each of the languages, based on length and multi-reference filters.
    Also identifies "complete" samples (i.e., available in 24 languages) to generate the validation and test set.
    """
    by_language_valid_ids = {}
    print("Compute language-specific valid samples...")
    for lang in tqdm(langs):
        by_language_valid_ids[lang] = get_valid_keys_for_language(data, language=lang)

    validation_test_candidates = set([sample["celex_id"] for sample in data])

    for _, valid_language_celex_ids in by_language_valid_ids.items():
        validation_test_candidates = validation_test_candidates.intersection(set(valid_language_celex_ids))
    print(f"{len(validation_test_candidates)} candidates suitable for validation/test set.")

    return by_language_valid_ids, list(validation_test_candidates)


def celex_text_sample(celex_id, texts):
    return {celex_id: {"reference_text": clean_text(texts["reference_text"]),
                       "summary_text": clean_text(texts["summary_text"])}}


if __name__ == '__main__':
    langs = ['french', 'german', 'english', 'spanish', 'italian', 'portuguese', 'greek', 'dutch', 'danish', 'finnish',
             'swedish', 'romanian', 'czech', 'polish', 'lithuanian', 'slovenian', 'latvian', 'bulgarian', 'estonian',
             'hungarian', 'slovak', 'maltese', 'croatian', 'irish']

    rng = np.random.default_rng(seed=12121994)
    write_valid_ids = False

    with open("offline_data_storage.pkl", "rb") as f:
        data = pickle.load(f)

    print(f"Checkpoint data is from {data['created_at']}.")
    print(f"Successfully loaded {len(data['samples'])} samples")
    data = data["samples"]

    # Enable this to get a list of all considered ids in the original corpus from 1990 - today.
    if write_valid_ids:
        all_celex_ids_until_1990 = [sample["celex_id"] for sample in data]

        with open("all_valid_celex_ids.json", "w") as f:
            json.dump(all_celex_ids_until_1990, f)

    # Print quick distribution
    count_total_number_instances(data)
    num_test_set_samples = sum([sample["for_test_set"] for sample in data])
    print(f"{num_test_set_samples} samples are suitable for usage in the validation/test set.")
    print(f"That is out of a total number of {len(data)} distinct samples.")

    lang_samples, validation_test_keys = identify_lang_ids(data, langs)

    # Iterate over samples to identify which cause issues
    # verify_samples(data, validation_test_keys, lang_samples)
    find_all_invalid_samples(data)

    # Randomize order to pick from
    rng.shuffle(validation_test_keys)

    validation_set = validation_test_keys[:len(validation_test_keys) // 2]
    test_set = validation_test_keys[len(validation_test_keys) // 2:]

    clean_data = {}
    for language in tqdm(langs):
        # Separate the ids into each of the corresponding sets.
        clean_data[language] = {"train": [], "validation": [], "test": []}

        for sample in data:
            # If the current sample is contained
            if sample["celex_id"] in lang_samples[language]:
                if sample["celex_id"] in validation_set:
                    clean_data[language]["validation"].append(celex_text_sample(sample["celex_id"], sample[language]))
                elif sample["celex_id"] in test_set:
                    clean_data[language]["test"].append(celex_text_sample(sample["celex_id"], sample[language]))
                else:
                    clean_data[language]["train"].append(celex_text_sample(sample["celex_id"], sample[language]))

    del data
    time.sleep(2)
    with open("clean_data.pkl", "wb") as f:
        pickle.dump(clean_data, f)
