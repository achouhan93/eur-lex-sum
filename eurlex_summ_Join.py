# Importing all requried packages

import logging
import os
import re
import urllib.request
from time import sleep, time

import requests
import pandas as pd
from bs4 import BeautifulSoup

# For Uni Heidelberg Server
from opensearchpy import OpenSearch

# For Localhost
from elasticsearch import Elasticsearch

#####################################################################################################
# Directory Creation
# For logging the progress of the script and the list of Celex Numbers extracted
#####################################################################################################
working_dir = os.getcwd()   
directory = os.path.join(working_dir, 'Scrapped_Data')

if not os.path.exists(directory):
    os.makedirs(directory)

filename_celex = os.path.join(directory, 'Celex_Numbers.csv')

# Preparing a File to Log the Metadata Informaiton
extraction_logs = os.path.join(directory, 'Logs_Extracting_MetaData.log')

def extract_document_information(es, index_name):
    # """"""""""
    # Functionality: Check if the document is already present in the index
    #
    # Signature of the function:
    #  Input: 
    #       esIndex: ElasticSearch or OpenSearch connection
    #       indexName: Name of the index that needs to be created
    #       celexList: List of the celex number for which the summary and content needs to be extracted
    # 
    #  Output:
    #       nonExisting: List of all the celex number that are not present in the ElasticSearch or OpenSearch index
    # """"""""""
    results = es.search(index= index_name)
    document_size = results['hits']['total']['value']
    results = es.search(index= index_name, size = document_size)
    
    result_list = [(i["_id"], i["_source"]["content"]) for i in results["hits"]["hits"]]
    documents = pd.DataFrame(result_list, columns=['celex_id', 'content'])
    return documents

def elastic_document_summary_information(es, index_name):
    # """"""""""
    # Functionality: Check if the document is already present in the index
    #
    # Signature of the function:
    #  Input: 
    #       esIndex: ElasticSearch or OpenSearch connection
    #       indexName: Name of the index that needs to be created
    #       celexList: List of the celex number for which the summary and content needs to be extracted
    # 
    #  Output:
    #       nonExisting: List of all the celex number that are not present in the ElasticSearch or OpenSearch index
    # """"""""""
    document_summary_query = {
        "query":{
            "nested": {
            "path": "english",
            "query": {
                "nested": {
                "path": "english.summaryInformation",
                "query": {
                    "bool": {
                    "must_not": [
                        {"match": 
                        {
                        "english.summaryInformation.summaryContent": "NA"
                        }
                        }
                    ]
                    }
                }
                }
            }
            }
        }
    }
    
    results = es.search(index= index_name, body = document_summary_query)
    document_summary_size = results['hits']['total']['value']
    results = es.search(index= index_name, body = document_summary_query, size = document_summary_size)

    summary_list = [(i["_id"], i["_source"]["english"]["summaryInformation"]["summaryContent"]) for i in results["hits"]["hits"]]
    summary = pd.DataFrame(summary_list, columns=['celex_id', 'summary'])
    return summary

def document_combining(document_information, document_summary_information):
    # """"""""""
    # Functionality: Check if the document is already present in the index
    #
    # Signature of the function:
    #  Input: 
    #       esIndex: ElasticSearch or OpenSearch connection
    #       indexName: Name of the index that needs to be created
    #       celexList: List of the celex number for which the summary and content needs to be extracted
    # 
    #  Output:
    #       nonExisting: List of all the celex number that are not present in the ElasticSearch or OpenSearch index
    # """"""""""
    documents_combined = pd.merge(document_information, document_summary_information, on = "celex_id")
    return documents_combined

def elastic_search_mapping():
    # """"""""""
    # Functionality: Creation of the mapping for the ElasticSearch or OpenSearch Index
    # 
    # For this project mapping is created from JSON using https://json-to-es-mapping.netlify.app/
    #
    # Signature of the function:
    #  Input: 
    #       No input is required for this function, as it is executed to create an object for mapping
    # 
    #  Output:
    #       es_mapping: Mapping setting for the ElasticSearch or OpenSearch Index
    # """""""""" 
    es_mapping = {
        "settings": {
            "number_of_shards":1,
            "number_of_replicas":0
        },
        "mappings": {
            "properties": {
                "documentContent": {
                    "type": "text"
                }, 
                "documentSummary": {
                    "type": "text"
                }
            }
        }
    }

    return es_mapping

def elastic_search_create(es_index, index_name, es_mapping):
    # """"""""""
    # Functionality: Creation of the Index if not present in the cluster
    # 
    # Signature of the function:
    #  Input: 
    #       esIndex: ElasticSearch or OpenSearch connection
    #       indexName: Name of the index that needs to be created
    #       esMapping: Mapping of the index that needs to be created
    # 
    #  Output:
    #       If the index is already present then the function wont take any action
    #       And if the index is not present then it will be created by the function
    # """"""""""
    search_index = es_index.indices.exists(index=index_name)

    if search_index == False:
        es_index.indices.create(index=index_name, ignore=[400,404], body=es_mapping)

def elastic_search_insert(es_index, index_name, celex_information):
    # """"""""""
    # Functionality: Insert the document in the ElasticSearch or OpenSearch Index
    #
    # Signature of the function:
    #  Input: 
    #       esIndex: ElasticSearch or OpenSearch connection
    #       indexName: Name of the index that needs to be created
    #       celexInformation: Information that needs to be inserted in the Index in JSON format
    # 
    #  Output:
    #       Insert the information in the ElasticSearch or OpenSearch Index keeping unqiue ID (_id) as the celex number
    # """"""""""
    for id, row in celex_information.iterrows():
        doc = { 
            "documentContent": row['content'],
            "documentSummary": row['summary']
            }
        _id = row['celex_id']
        
        retries = 0
        while True:
            try:
                es_index.index(index=index_name,body=doc,id=_id)
                break
            except Exception as e:
                if retries == 5:
                    print('Indexing user \'{}\' failed for 5 consecutiv times. Aborting!'.format(_id))
                    break
                retries += 1
                sleep(retries * 5)

def elastic_search_existing_check(es_index, index_name, celex_list):
    # """"""""""
    # Functionality: Check if the document is already present in the index
    #
    # Signature of the function:
    #  Input: 
    #       esIndex: ElasticSearch or OpenSearch connection
    #       indexName: Name of the index that needs to be created
    #       celexList: List of the celex number for which the summary and content needs to be extracted
    # 
    #  Output:
    #       nonExisting: List of all the celex number that are not present in the ElasticSearch or OpenSearch index
    # """"""""""
    non_existing = []
    for celex_id in celex_list:
        document_status = es_index.exists(index= index_name, id= celex_id)
        if document_status == False:
            non_existing.append(celex_id)
    
    return non_existing

if __name__ == '__main__':

    # Configuring the File name to logging Level
    logging.basicConfig(filename=extraction_logs,level=logging.INFO)

    document_information = pd.DataFrame(data=None)
    document_summary_information = pd.DataFrame(data=None)
    document_combined_information = pd.DataFrame(data=None)

    start_time = time()
    logging.info("Current date and time for Joining Script: " + str(start_time))

    # Elastic Search Index
    index_name_join = 'eur-lex-data'
    index_name_document = 'achouhan'
    index_name_summary = 'eur-lex-sum'

    # Instance of Elastic Search
    user_name = os.environ.get('UNI_USER')
    password = os.environ.get('UNI_PWD')
    es = OpenSearch(hosts = [{'host': 'elastic-dbs.ifi.uni-heidelberg.de', 'port': 443}], 
    http_auth =(user_name, password), 
    use_ssl = True,
    verify_certs = True,
    ssl_assert_hostname = False,
    ssl_show_warn = False
    )
        
    # Calling the Function for the given CELEX_Numbers
    document_information = extract_document_information(es, index_name_document)
    document_summary_information = elastic_document_summary_information(es, index_name_summary)
    document_combined_information = document_combining(document_information, document_summary_information)

    es_index_mapping = elastic_search_mapping()
    elastic_search_create(es, index_name_join, es_index_mapping)

    list_celex_number = document_combined_information['celex_id'].values.tolist()
    non_existing_celex_number = elastic_search_existing_check(es, index_name_join, list_celex_number)

    elastic_search_insert(es, index_name_join, document_combined_information)

    end_time = time()
    logging.info("Current date and time for Joining Script: " + str(end_time))
    logging.info("Time for Execution of Script of Joining Script: " + str(start_time - end_time))