from typing import List, Dict
from collections import Counter, defaultdict
from datetime import datetime
import regex

import numpy as np
from tqdm import tqdm
from opensearchpy import OpenSearch

from config import USER, PASSWORD


def update_document_language_distribution(response: Dict, collect_occurrences: List):

    # Iterate through the documents and count availability of languages
    documents = response["hits"]["hits"]

    for document in tqdm(documents):
        for language, doc_info in document["_source"].items():
            # Check for cases were mismatch of N/A data is found wrt the summary
            if doc_info["documentInformation"]["documentContent"] == "NA" and \
               doc_info["documentInformation"]["summaryContent"] != "NA":
                # raise AssertionError(f"Document summary is non-empty for non-existent document "
                #                      f"{document['_id']} ({language})")
                print(f"Found non-empty summary for empty document {document['_id']} ({language})")
            # Otherwise, this is all good
            elif doc_info["documentInformation"]["documentContent"] != "NA" and \
                 doc_info["documentInformation"]["summaryContent"] != "NA":
                collect_occurrences.append(language)


def analyze_text_lengths(response: Dict, reference_lengths: Dict, summary_lengths: Dict, compression_ratios: Dict):
    # Iterate through the documents and count availability of languages
    documents = response["hits"]["hits"]

    for document in tqdm(documents):
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

    # Replace misplaced utf8 chars
    text = text.replace(u"\xa0", u" ")

    # Use two or more consecutive newlines as a preliminary split decision
    text = regex.sub(r"\n{2,}", r"[SPLIT]", text)
    split_text = text.split("[SPLIT")

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


def compute_whitespace_split_length(text: str):
    return len(text.split(" "))


if __name__ == '__main__':
    print(f"Started at {datetime.now()}")
    index_name = "eur-lex-multilingual"

    client = OpenSearch([{'host': 'elastic-dbs.ifi.uni-heidelberg.de', 'port': 443}],
                        http_auth=(USER, PASSWORD),
                        use_ssl=True,
                        http_compress=True,
                        verify_certs=False,
                        ssl_assert_hostname=False,
                        ssl_show_warn=False)

    # Get relevant documents to determine pagination:
    response = client.search(body={}, index=index_name, size=0)
    # Number of documents found
    total_docs = response["hits"]["total"]["value"]
    print(f"{total_docs} documents found")

    batch_size = 50
    languages_with_non_empty_docs = []

    reference_token_lengths = defaultdict(list)
    summary_token_lengths = defaultdict(list)
    compression_ratios = defaultdict(list)

    for start in range(0, total_docs, batch_size):
        response = client.search(body={}, index=index_name, size=batch_size, from_=start)

        update_document_language_distribution(response, languages_with_non_empty_docs)
        analyze_text_lengths(response, reference_token_lengths, summary_token_lengths, compression_ratios)

    language_distribution = Counter(languages_with_non_empty_docs)
    for language, frequency in language_distribution.most_common():
        print(f"{language} & {frequency} \\\\")

    for language in reference_token_lengths.keys():
        if language not in ["german", "english", "french"]:
            continue
        print(f"#######################################\n"
              f"Stats for {language}:")
        print(f"Mean reference length: {np.mean(reference_token_lengths[language]):.2f} "
              f"+/- {np.std(reference_token_lengths[language]):.2f}")
        print(f"Median reference length: {np.median(reference_token_lengths[language]):.2f}\n")

        print(f"Mean summary length: {np.mean(summary_token_lengths[language]):.2f} "
              f"+/- {np.std(summary_token_lengths[language]):.2f}")
        print(f"Median summary length: {np.median(summary_token_lengths[language]):.2f}\n")

        print(f"Mean compression ratio: {np.mean(compression_ratios[language])}\n\n")





