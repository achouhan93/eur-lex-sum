"""
Script to compute the basic length stats of the different language-specific corpora.
"""

from typing import List, Dict, Union, Tuple, Optional
from collections import Counter, defaultdict
from datetime import datetime
import regex

import numpy as np
from tqdm import tqdm
from opensearchpy import OpenSearch
from opensearchpy.helpers import scan
import matplotlib
import matplotlib.pyplot as plt

from config import USER, PASSWORD


def update_document_language_distribution(document: Dict, collect_occurrences: List) -> None:

    # Iterate through the documents and count availability of languages
    for language, doc_info in document["_source"].items():
        # Check for cases were mismatch of N/A data is found wrt the summary
        if doc_info["documentInformation"]["documentContent"] == "NA" and \
           doc_info["documentInformation"]["summaryContent"] != "NA":
            # We only care about non-irish exceptions.
            if language != "irish":
                print(f"Found non-empty summary for empty document {document['_id']} ({language})")
        # Otherwise, this is all good
        elif doc_info["documentInformation"]["documentContent"] != "NA" and \
                doc_info["documentInformation"]["summaryContent"] != "NA":
            collect_occurrences.append(language)


def analyze_text_lengths(document: Dict, reference_lengths: Dict, summary_lengths: Dict, compression_ratios: Dict) \
        -> None:

    # Only consider documents that are available in at least 23 languages
    available_languages = 0
    for _, doc_info in document["_source"].items():
        if doc_info["documentInformation"]["documentContent"] != "NA" and \
                doc_info["documentInformation"]["summaryContent"] != "NA":
            available_languages += 1

    if available_languages < 23:
        return None

    for language, doc_info in document["_source"].items():
        # Skip any document that doesn't have a pair of content and summary
        if doc_info["documentInformation"]["documentContent"] == "NA" or \
           doc_info["documentInformation"]["summaryContent"] == "NA":
            continue

        reference = doc_info["documentInformation"]["documentContent"]
        summary = doc_info["documentInformation"]["summaryContent"]

        reference_length = compute_whitespace_split_length(clean_text(reference))
        # Add tokenized length of reference
        reference_lengths[language].append(reference_length)
        # Add tokenized length of summary
        summary_length = compute_whitespace_split_length(clean_text(summary))
        summary_lengths[language].append(summary_length)
        # Compute compression ratio
        compression_ratios[language].append(reference_length / summary_length)


def clean_text(text: str) -> str:
    """
    Internally converts the text to a simple paragraph estimate, and re-joins it after simple cleaning operations.
    """

    split_text = get_split_text(text)

    # Remove empty lines and the XML identifier in some first line
    split_text = [line.strip() for line in split_text if line.strip() and not line.endswith(".xml")]
    # TODO: Merge and remove lines based on further heuristics to clean up
    # for line in split_text:
    #     # Check for short lines
    #     if len(line.split(" ")) < 4:
    #         # Skip the first line which contains a .xml file name
    #         if line.endswith(".xml"):
    #             continue
    #         # If digits are present, it is likely a match with the previous line
    #         elif regex.findall(r"[0-9]", line):
    #             continue
    #         # Or if we find other "item-like" characters, such as "a)" or "b)"
    #         elif regex.match(r"[a-z])", line):

    text = " ".join(split_text).replace("\n", " ")
    return text


def get_split_text(text: str) -> List[str]:
    """
    Utility function to generate pseudo-paragraph splitting
    """
    # Replace misplaced utf8 chars
    text = text.replace(u"\xa0", u" ")

    # Use two or more consecutive newlines as a preliminary split decision
    text = regex.sub(r"\n{2,}", r"[SPLIT]", text)
    split_text = text.split("[SPLIT]")
    return split_text


def compute_whitespace_split_length(text: str) -> int:
    return len(text.split(" "))


def print_language_stats(language: str,
                         reference_lengths: Dict[str, List[int]],
                         summary_lengths: Dict[str, List[int]],
                         compression_ratios: Dict[str, List[float]]) -> None:
    print(f"#######################################\n"
          f"Stats for {language}:")
    print_dist(reference_lengths[language], "reference lengths")
    print_dist(summary_lengths[language], "summary lengths")
    print_dist(compression_ratios[language], "compression ratio")


def print_dist(lengths: List[Union[int, float]], description: str) -> None:
    print(f"Mean {description}: {np.mean(lengths[language]):.2f} "
          f"+/- {np.std(lengths[language]):.2f}")
    print(f"Median {description}: {np.median(lengths[language]):.2f}\n")
    print(f"Minimum length of {description}: {np.min(lengths[language]):.2f}\n"
          f"Maximum length of {description}: {np.max(lengths[language]):.2f}")


def histogram_plot(lengths: List[int],
                   language: str,
                   type_of_lengths: str,
                   xlim: Optional[Union[List, Tuple]] = (0, 20000),
                   ylim: Optional[Union[List, Tuple]] = (0, 150),
                   bins: int = 20,
                   fp: str = "./Insights/histogram.png"
                   ):
    plt.hist(lengths, range=xlim, bins=bins, color='#1b9e77')
    plt.xlim(xlim)
    plt.ylim(ylim)

    # Mean and std lines
    plt.axvline(np.mean(lengths), color='k', linestyle='dashed', linewidth=2)
    plt.axvline(np.mean(lengths) - np.std(lengths), color='k', linestyle='dotted', linewidth=1)
    plt.axvline(np.mean(lengths) + np.std(lengths), color='k', linestyle='dotted', linewidth=1)
    # Median line
    plt.axvline(np.median(lengths), color='#d95f02', linestyle='solid', linewidth=2)
    plt.title(f"Histogram of {type_of_lengths} length of {language}")
    plt.savefig(fp)
    plt.show()
    plt.close()


def compare_en_de_texts(document: Dict):

    en_ref = ""
    en_summ = ""
    de_ref = ""
    de_summ = ""
    for language, doc_info in document["_source"].items():
        if language not in ["german", "english"]:
            continue

        if doc_info["documentInformation"]["documentContent"] != "NA" and \
                doc_info["documentInformation"]["summaryContent"] != "NA":
            # Replace misplaced utf8 chars
            ref_text = get_split_text(doc_info["documentInformation"]["documentContent"])
            summary_text = get_split_text(doc_info["documentInformation"]["summaryContent"])

            if language == "german":
                de_ref = ref_text
                de_summ = summary_text
            elif language == "english":
                en_ref = ref_text
                en_summ = summary_text

    if de_summ and en_summ:
        print("Reference text alignments")
        for en_block, de_block in zip(en_ref, de_ref):
            print(en_block)
            print(de_block)
            print("\n\n\n")

        print("\n\n\n\n\nSummary text alignments")
        for en_block, de_block in zip(en_summ, de_ref):
            print(en_block)
            print(de_block)
            print("\n\n\n")


if __name__ == '__main__':
    # Set correct font size for plots
    matplotlib.rc('xtick', labelsize=18)
    matplotlib.rc('ytick', labelsize=18)
    # set LaTeX font
    matplotlib.rcParams['mathtext.fontset'] = 'stix'
    matplotlib.rcParams['font.family'] = 'STIXGeneral'

    # Reference time to compare number of available articles
    print(f"Started at {datetime.now().isoformat()}")
    index_name = "eur-lex-multilingual"

    # Open connection to Opensearch database
    client = OpenSearch([{'host': 'elastic-dbs.ifi.uni-heidelberg.de', 'port': 443}],
                        http_auth=(USER, PASSWORD),
                        use_ssl=True,
                        http_compress=True,
                        verify_certs=False,
                        ssl_assert_hostname=False,
                        ssl_show_warn=False)

    batch_size = 50
    languages_with_non_empty_docs = []

    # Will store information in a list per language
    reference_token_lengths = defaultdict(list)
    summary_token_lengths = defaultdict(list)
    compression_ratios = defaultdict(list)

    # Batch-processing of the available articles with scan()
    for response in tqdm(scan(query={}, client=client, index=index_name, size=batch_size, request_timeout=50)):

        update_document_language_distribution(response, languages_with_non_empty_docs)
        analyze_text_lengths(response, reference_token_lengths, summary_token_lengths, compression_ratios)

    # use the final batch to compare a sample reference and summary
    compare_en_de_texts(response)

    language_distribution = Counter(languages_with_non_empty_docs)
    x_label = []
    y = []

    language_string = ""
    frequency_string = ""
    for language, frequency in language_distribution.most_common():
        language_string += f"{language} & "
        frequency_string += f"{frequency} & "
        x_label.append(language)
        y.append(frequency)

    print(f"{language_string}\n{frequency_string}")

    for language in reference_token_lengths.keys():
        # For reference, ignore information on other languages for legibility
        if language not in ["german", "english", "french"]:
            continue

        print_language_stats(language, reference_token_lengths, summary_token_lengths, compression_ratios)

        histogram_plot(reference_token_lengths[language], language, "reference",
                       xlim=[0, 30000],
                       fp=f"./Insights/histogram-reference-{language}.png")
        histogram_plot(summary_token_lengths[language], language, "summary",
                       xlim=[0, 3000],
                       fp=f"./Insights/histogram-summary-{language}.png")

    x_value = [3*i for i in range(len(x_label))]
    plt.bar(x_value, y, color='#1b9e77', width=2.6)
    # Use language codes for better readability
    x_label = ["en", "es", "de", "fr", "it", "dk", "nl", "pt", "ro", "fi", "sw", "bg", "el", "li", "hu", "cz", "et",
               "lt", "po", "sk", "sl", "mt", "cr", "ga"]
    plt.xticks(x_value, x_label, rotation=90)
    plt.xlim([-2, max(x_value)+2])

    fig = plt.gcf()
    fig.set_figwidth(16)

    plt.savefig("./Insights/language_distribution.png", dpi=400, bbox_inches="tight")
    plt.show()
