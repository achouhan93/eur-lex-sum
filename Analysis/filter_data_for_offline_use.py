"""
Script to write an offline copy of the data for faster retrieval.
Performs preliminary filtering such that all languages are non-empty.
"""
from typing import Dict
from datetime import datetime
import pickle

from tqdm import tqdm
from opensearchpy import OpenSearch
from opensearchpy.helpers import scan

from config import USER, PASSWORD


def has_all_relevant_languages_available(response_doc: Dict) -> bool:
    available_langs = set()
    for language, doc_info in response_doc["_source"].items():
        # Check that both reference and summary text are available in that language
        if doc_info["documentInformation"]["documentContent"] != "NA" and \
           doc_info["documentInformation"]["summaryContent"] != "NA" and \
           language != "irish":
            available_langs.add(language)

    # Without irish, there are 23 official languages. Other samples will be dropped (less than 100)
    if len(available_langs) == 23:
        return True
    else:
        return False


def add_to_sample_store(response_doc: Dict, index: Dict) -> None:

    sample_template = {
        "celex_id": response_doc["_id"],
        "for_test_set": is_suitable_for_test_set(response_doc),
    }

    # Add the language content in a less nested way
    for language, doc_info in response_doc["_source"].items():
        sample_template[language] = {
            "reference_text": doc_info["documentInformation"]["documentContent"],
            "summary_text": doc_info["documentInformation"]["summaryContent"]
        }
    index["samples"].append(sample_template)


def is_suitable_for_test_set(response_doc: Dict) -> bool:
    """
    We want to only use documents that also have irish data available as test samples,
    since they are the least likely language.
    """
    if response_doc["_source"]["irish"]["documentInformation"]["documentContent"] != "NA" and \
       response_doc["_source"]["irish"]["documentInformation"]["summaryContent"] != "NA":
        return True
    else:
        return False


if __name__ == '__main__':
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

    valid_sample_store = {
        "created_at": datetime.now().isoformat(timespec="minutes"),
        "samples": []
    }

    # Batch-processing of the available articles with scan()
    for doc in tqdm(scan(query={}, client=client, index=index_name, size=batch_size, request_timeout=50)):

        # Only add if all 23 languages are available
        if has_all_relevant_languages_available(doc):
            add_to_sample_store(doc, valid_sample_store)

    input("All data samples saved, please confirm to save file.")

    with open("offline_data_storage.pkl", "wb") as f:
        pickle.dump(valid_sample_store, f)
    print(f"Successfully wrote {len(valid_sample_store['samples'])} samples to disk.")
