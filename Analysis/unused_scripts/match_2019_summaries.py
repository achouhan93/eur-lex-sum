"""
Confirm which of the documents that actually do have a summary (and should therefore be available)
are in the crawled corpus. This reveals a few documents with different properties that are excluded.

If running this, make sure to have a valid configuration file in the same folder.
"""

import requests
import time

from lxml import html
from tqdm import tqdm
from opensearchpy import OpenSearch

from config import USER, PASSWORD


if __name__ == '__main__':
    base_url = "https://eur-lex.europa.eu/search.html?OBSOLETE_LEGISUM=false&DTS_SUBDOM=EU_LEGI_SUM&" \
               "type=advanced&qid=1653286109259&SUBDOM_INIT=EU_LEGI_SUM&scope=EU_SUMMARY&SUM_DD_YEAR=2019&page="

    candidate_list = []
    for i in tqdm(range(1, 25)):
        req_url = f"{base_url}{i}"

        res = requests.get(req_url)

        tree = html.fromstring(res.content)

        # Traverse the tree of results
        per_summary_docs = tree.xpath("//div[contains(@class, 'SearchResultData collapse in')]/div/div/dl/dd/ul")

        for doc in per_summary_docs:
            candidate_list.append([element.text for element in doc.xpath("li/a")])

        time.sleep(0.8)

    # Compare to the available documents:
    # Open connection to Opensearch database
    client = OpenSearch([{'host': 'elastic-dbs.ifi.uni-heidelberg.de', 'port': 443}],
                        http_auth=(USER, PASSWORD),
                        use_ssl=True,
                        http_compress=True,
                        verify_certs=False,
                        ssl_assert_hostname=False,
                        ssl_show_warn=False)

    index_name = "eur-lex-multilingual"

    stored_candidates = []
    batch_size = 100
    for offset in tqdm(range(0, 6800, batch_size)):
        response = client.search(body={}, index=index_name, size=batch_size, from_=offset, _source={"_id"})

        stored_candidates.extend([element["_id"] for element in response["hits"]["hits"]])

    relevant_start_char = {"2", "3", "4"}
    for reference_docs in candidate_list:
        found_relevant_doc = False
        # Check whether the element is considered appropriate (starts with a "2/3/4")
        for summarized_doc in reference_docs:
            if summarized_doc[0] not in relevant_start_char:
                continue

            # Found a matching entry, thus the document is present in our available corpus
            if summarized_doc in stored_candidates:
                found_relevant_doc = True

        if not found_relevant_doc:
            print(f"Did not find a suitable candidate for the document with references {reference_docs}")








