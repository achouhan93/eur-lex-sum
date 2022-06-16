"""
Compute stats such as compression ratio, lengths, n-gram novelty, etc.
"""
from typing import List, Union, Set

import pickle
import numpy as np

from utils import compute_whitespace_split_length, histogram_plot


def compute_char_lengths(samples, key: str) -> List[int]:
    lengths = []
    for celex_id, sample in samples.items():
        lengths.append(len(sample[key]))

    return lengths


def compute_whitespace_token_lengths(samples, key: str) -> List[int]:
    lengths = []
    for _, sample in samples.items():
        lengths.append(compute_whitespace_split_length(sample[key]))

    return lengths


def print_latex(lengths: List[Union[int, float]], description: str) -> None:
    print(f"{description}:\t{np.mean(lengths):.2f} $\\pm$ {np.std(lengths):.2f} & {np.median(lengths):.2f} & "
          f"{np.min(lengths):.2f} & {np.max(lengths):.2f} \\\\")
    # print(f"Mean {description}:\t\t\t{np.mean(lengths):.2f} "
    #       f"+/- {np.std(lengths):.2f}")
    # print(f"Median {description}:\t\t{np.median(lengths):.2f}")
    # print(f"Minimum length of {description}:\t{np.min(lengths):.2f}\n"
    #       f"Maximum length of {description}:\t{np.max(lengths):.2f}\n\n")


def get_novel_ngrams(samples, max_ngram_length: int = 4):
    novel_ratios = []

    for n in range(1, max_ngram_length + 1):
        all_ratios = []
        for _, sample in samples.items():
            reference_ngrams = get_ngrams(sample["reference_text"], n)
            summary_ngrams = get_ngrams(sample["summary_text"], n)

            all_ratios.append(novelty_ratio(reference_ngrams, summary_ngrams))

        novel_ratios.append(np.mean(all_ratios))

    return novel_ratios


def get_ngrams(text, n):
    n_grams = set()
    tokens = text.split(" ")

    for pos in range(len(tokens[:-n])+1):
        n_grams.add(tuple(tokens[pos:pos+n]))

    return n_grams


def novelty_ratio(reference: Set, summary: Set):
    return 1 - (len(summary.intersection(reference)) / len(summary))


if __name__ == '__main__':
    with open("clean_data.pkl", "rb") as f:
        data = pickle.load(f)

    for lang, all_data in data.items():

        print(f"Stats for {lang}")
        for split, samples in all_data.items():

            ref_char_lengths = compute_char_lengths(samples, "reference_text")
            summ_char_lengths = compute_char_lengths(samples, "summary_text")

            ref_token_lengths = compute_whitespace_token_lengths(samples, "reference_text")
            summ_token_lengths = compute_whitespace_token_lengths(samples, "summary_text")

            # TODO: Compression ratio
            char_compression_ratios = [ref_length / summ_length for ref_length, summ_length in zip(ref_char_lengths,
                                                                                                   summ_char_lengths)]
            token_compression_ratios = [ref_length / summ_length for ref_length, summ_length in zip(ref_token_lengths,
                                                                                                    summ_token_lengths)]

            print_latex(ref_char_lengths, "reference char")
            print_latex(summ_char_lengths, "summary char")
            print_latex(char_compression_ratios, "compression ratios char")
            print_latex(ref_token_lengths, "reference token")
            print_latex(summ_token_lengths, "summary token")
            print_latex(token_compression_ratios, "compression ratios token")

            # FIXME: Should this be validation or test set instead?
            #  Or maybe all of them?
            if lang == "english" and split == "train":
                print(f"ref length max: {max(ref_token_lengths)}")
                print(f"summ length max: {max(summ_token_lengths)}")
                print(f"compression ratio max: {max(token_compression_ratios)}")

                print(f"ref length 95: {np.percentile(ref_token_lengths, 95)}")
                print(f"summ length 95: {np.percentile(summ_token_lengths, 95)}")
                print(f"compression ratio 95: {np.percentile(token_compression_ratios, 95)}")
                # TODO: Remove standard deviation in plots?
                histogram_plot(ref_token_lengths, language="English", type_of_lengths="Length of reference text",
                               xlim=(0, 40000), ylim=(0, 175), bins=40, fp="./Insights/histogram_en_reference.png")
                histogram_plot(summ_token_lengths, language="English", type_of_lengths="Length of summary text",
                               xlim=(0, 1600), ylim=(0, 175), bins=40, fp="./Insights/histogram_en_summary.png")
                histogram_plot(token_compression_ratios, language="English", type_of_lengths="Compression ratio",
                               xlim=(0, 40), ylim=(0, 175), bins=40, fp="./Insights/histogram_en_ratios.png")

            # TODO: Novelty Ngrams
            novel_ratio_for_language = get_novel_ngrams(samples, max_ngram_length=4)
            ratio_string = f"Novel n-gram ratios: "
            for ratio in novel_ratio_for_language:
                ratio_string += f"& {ratio*100:.2f} "

            print(ratio_string)

            print("\n\n")
            # TODO: Oracle extractive baseline

            # TODO: Get age distribution from celex


