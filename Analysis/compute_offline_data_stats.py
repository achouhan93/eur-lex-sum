"""
Based on the (filtered) corpus of offline data, compute stats
"""

import regex
import pickle
from difflib import SequenceMatcher

from tqdm import tqdm
import spacy
import numpy as np

from utils import clean_text, compute_whitespace_split_length, print_language_stats


if __name__ == '__main__':
    with open("offline_data_storage.pkl", "rb") as f:
        data = pickle.load(f)

    print("Successfully loaded samples")
    data = data["samples"]

    # For now only compute stats for English

    reference_texts = [sample["english"]["reference_text"] for sample in data]
    summary_texts = [sample["english"]["summary_text"] for sample in data]
    celex_ids = [sample["celex_id"] for sample in data]
    print("Extracted texts")

    del data

    # Loads with disabled components only suitable for tokenization
    nlp = spacy.load("en_core_web_sm")
    print("Starting reference processing")
    # FIXME: Currently crashes due to memory issues, since some documents are extremely long.
    # reference_token_lengths = [len(doc) for doc in nlp.pipe(reference_texts,
    #                                                         disable=['parser', 'tagger', 'ner'],
    #                                                         batch_size=5)]
    # summary_token_lengths = [len(doc) for doc in nlp.pipe(summary_texts,
    #                                                       disable=['parser', 'tagger', 'ner'],
    #                                                       batch_size=50)]

    reference_token_lengths = [compute_whitespace_split_length(clean_text(text)) for text in tqdm(reference_texts)]
    summary_token_lengths = [compute_whitespace_split_length(clean_text(text)) for text in tqdm(summary_texts)]

    compression_ratios = [reference_token_lengths[i] / summary_token_lengths[i] for i in range(len(reference_texts))]

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


    ref_text_scans = []
    summ_text_scans = []

    # Filter documents that are likely document scans
    for celex_id, ref_text, summ_text in zip(celex_ids, reference_texts, summary_texts):
        if "[NEW PAGE]" in ref_text:
            print(f"{celex_id} contains [NEW PAGE] in the reference text")
            # print(ref_text[:500])
            ref_text_scans.append(celex_id)

        if "[NEW PAGE]" in summ_text:
            print(f"{celex_id} contains [NEW PAGE] in the summary text")
            # print(ref_text[:500])
            summ_text_scans.append(celex_id)

    print(f"{len(ref_text_scans)} reference texts are likely document scans.")
    print(f"{len(summ_text_scans)} summary texts are likely document scans.")

    # # Manually review some of the short reference texts to spot errors
    # for celex_id, ref_text, ref_length in zip(celex_ids, reference_texts, reference_token_lengths):
    #     if ref_length < 500:
    #         print(celex_id)
    #         print(ref_text)
    #         input("Press a button to continue...")

    # Evaluate how many docs are potentially affected by "really short" documents:

    print(f"Length of shortest 5% of reference articles: {np.percentile(reference_token_lengths, 5)} tokens")
    print(f"Length of shortest 5% of *summary* articles: {np.percentile(summary_token_lengths, 5)} tokens")

    print(f"Length of shortest 10% of reference articles: {np.percentile(reference_token_lengths, 10)} tokens")
    print(f"Length of shortest 10% of *summary* articles: {np.percentile(summary_token_lengths, 10)} tokens")

    # Evaluate which fraction of docs is affected by multiple summaries
    more_than_two = []
    exactly_two = []
    no_summary_of_found = []
    for celex_id, ref_text, summ_text, ref_length, summ_length in zip(celex_ids, reference_texts, summary_texts,
                                                                      reference_token_lengths, summary_token_lengths):

        # Lazy match the section of interest
        # Matching more documents
        summary_of_segment = regex.search(r"(SUMMARY OF:?|ACT)(.*?)(SUMMARY|WHAT IS|WHAT ARE|WHAT DOES)",
                                          summ_text, regex.DOTALL)
        if summary_of_segment:
            group_text = summary_of_segment[2].strip("\n ")
            num_relevant_segments = len(group_text.split("\n\n\n"))

            if num_relevant_segments > 2:
                # print(f"{celex_id} has more than two reference documents")
                more_than_two.append(celex_id)
            elif num_relevant_segments == 2:
                # print(f"{celex_id} has exactly two reference documents")
                exactly_two.append(celex_id)
        else:
            no_summary_of_found.append(celex_id)

    print(f"{len(more_than_two)} documents have more than two reference documents.")
    print(f"{len(exactly_two)} documents have exactly two reference documents.")
    print(f"This makes {(len(more_than_two) + len(exactly_two)) / len(reference_texts) * 100:.2f}% of documents.")
    print(f"For {len(no_summary_of_found)} documents, no 'SUMMARY OF' section could be found.")

    # Figure out how many duplicate summaries we have in the corpus
    # This is quite inefficient O(N²) comparisons of long texts.
    # There is a different number of matches if we proxy by only using the length, which is why I would not recommend.
    duplicated_summaries = set()
    for celex_id, summ_text, summ_length in tqdm(zip(celex_ids, summary_texts, summary_token_lengths)):
        for other_celex_id, other_summ_text, other_summ_length in zip(celex_ids, summary_texts, summary_token_lengths):

            # seq = SequenceMatcher(None, summ_text, other_summ_text)
            if celex_id != other_celex_id and summ_text == other_summ_text:  # seq.ratio() > 0.95:
                # print(f"{celex_id} and {other_celex_id} have the same summary")
                # Sort by celex ID to avoid adding the reverse later on.
                duplicated_summaries.add(celex_id)

    print(f"{len(duplicated_summaries)} texts are affected by duplicated summaries.")

    # Find the difference between the previously identified articles
    multiple_sources = set(more_than_two).union(set(exactly_two))

