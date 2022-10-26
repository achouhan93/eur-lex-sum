from extractors.libraries import *
from extractors import get_document_summary, get_file_by_id, elastic_search_insert

def get_document_information(es, index_name, celex_list):
    """
    Orchestrator function to extract the summary and document content for the provided Celex Number

    Args:
        celex_list (list): List of Celex number for which the summary and contents needs to be extracted

    Returns:
        list: Comprising of dictionary of information about the summary and document 
                content for the provided Celex Numbers in the different languages
    """
    langs = ['BG', 'ES', 'CS', 'DA', 'DE', 'ET', 'EL', 'EN', 'FR',
    'GA' , 'HR' , 'IT', 'LV', 'LT', 'HU', 'MT',
    'NL', 'PL', 'PT', 'RO', 'SK', 'SL', 'FI', 'SV']
    logging.info("Execution of Extraction of Summary for respective Celex Document - Started")

    # For Each CELEX_Number preparing the URL and extracting Info from Website
    for celex_id in tqdm(celex_list):
        celex_document_information = {}
        celex_document_information['_id'] = celex_id
        
        for lang in langs:
            language_document_information = {}

            # Calling the function to extract the summary content for the celex document
            summary_data = get_document_summary(lang, celex_id)

            # Calling the function to extract the document content for the celex document
            document_information = get_file_by_id(lang, celex_id)
            
            language_document_information['documentInformation'] = document_information
            language_document_information['summaryInformation'] = summary_data
            celex_document_information[lang] = language_document_information

            logging.info(f'Completed Extracting Information of {celex_id} for {lang}')
            sleep(1)     
        
        elastic_search_insert(es, index_name, celex_document_information)
        logging.info("Execution of Extraction of Summary for respective Celex Document - Ended")