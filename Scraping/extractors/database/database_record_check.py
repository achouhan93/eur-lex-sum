
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