from extractors.libraries import *

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