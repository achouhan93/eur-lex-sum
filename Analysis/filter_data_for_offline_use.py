"""
Script to write an offline copy of the data for faster retrieval.
Notably, this does *not* yet filter out all invalid samples.
See `investigate_offline_data.py` for further filtering.
"""

from typing import Dict
from datetime import datetime
import pickle
import json

from tqdm import tqdm
from opensearchpy import OpenSearch
from opensearchpy.helpers import scan

from config import USER, PASSWORD


def has_all_relevant_languages_available(response_doc: Dict) -> bool:
    """
    Will check whether documents and summaries are available in all 24 languages.
    Only those documents will later be considered for the validation and test set.
    """
    available_langs = set()
    for language, doc_info in response_doc["_source"].items():
        # Check that both reference and summary text are available in that language
        if document_not_empty(doc_info) and document_not_scan(doc_info, language, response_doc["_id"]):
            available_langs.add(language)

    if len(available_langs) == 24:
        return True
    else:
        return False


def has_at_least_one_summary_available(response_doc: Dict) -> bool:
    """
    Will check whether documents and summaries are available in all 24 languages.
    Only those documents will later be considered for the validation and test set.
    """
    available_langs = set()
    for language, doc_info in response_doc["_source"].items():
        # Check that both reference and summary text are available in that language
        if document_not_empty(doc_info):
            available_langs.add(language)

    if len(available_langs) > 0:
        return True
    else:
        return False


def add_to_sample_store(response_doc: Dict, index: Dict) -> None:

    sample_template = {
        "celex_id": response_doc["_id"],
        "for_test_set": has_all_relevant_languages_available(response_doc),
    }

    # Add the language content in a less nested way
    for language, doc_info in response_doc["_source"].items():
        # Only include the actual content if both reference and summary are available.
        if document_not_empty(doc_info) and document_not_scan(doc_info, language, response_doc["_id"]):
            sample_template[language] = {
                "reference_text": doc_info["documentInformation"]["documentContent"],
                "summary_text": doc_info["documentInformation"]["summaryContent"]
            }
    index["samples"].append(sample_template)


def document_not_empty(doc_info):
    if doc_info["documentInformation"]["documentContent"] != "NA" and \
       doc_info["documentInformation"]["summaryContent"] != "NA":
        return True
    else:
        return False


def document_not_scan(doc_info, language, celex_id, verbose=False):
    if "NEW PAGE" not in doc_info["documentInformation"]["documentContent"] and \
       "NEW PAGE" not in doc_info["documentInformation"]["summaryContent"]:
        return True
    else:
        if verbose:
            print(f"{celex_id} has scanned document for language '{language}'")
        return False


if __name__ == '__main__':
    # Reference time to compare number of available articles
    print(f"Started at {datetime.now().isoformat()}")
    index_name = "eur-lex-multilingual"

    # We might have pre-filtered IDs that should be taken into consideration
    try:
        with open("all_valid_celex_ids.json", "r") as f:
            pre_filtered_ids = set(json.load(f))
    except FileNotFoundError:
        pre_filtered_ids = None

    # Open connection to Opensearch database
    client = OpenSearch([{'host': 'elastic-dbs.ifi.uni-heidelberg.de', 'port': 443}],
                        http_auth=(USER, PASSWORD),
                        use_ssl=True,
                        http_compress=True,
                        verify_certs=False,
                        ssl_assert_hostname=False,
                        ssl_show_warn=False)

    batch_size = 50

    valid_sample_store = {
        "created_at": datetime.now().isoformat(timespec="minutes"),
        "samples": []
    }

    # Batch-processing of the available articles with scan()
    for doc in tqdm(scan(query={}, client=client, index=index_name, size=batch_size, request_timeout=50)):
        # Make sure we only take documents into consideration that have a summary
        if has_at_least_one_summary_available(doc):
            # If we have a pre-filtered list of IDs, use those to generate a reduced list
            if pre_filtered_ids:
                if doc["_id"] in pre_filtered_ids:
                    add_to_sample_store(doc, valid_sample_store)
            else:
                add_to_sample_store(doc, valid_sample_store)

    # Manual intervention avoids RAM-related issues.
    input("All data samples saved, please confirm to save file.")

    with open("offline_data_storage.pkl", "wb") as f:
        pickle.dump(valid_sample_store, f)
    print(f"Successfully wrote {len(valid_sample_store['samples'])} samples to disk.")
