from extractors.libraries import *

def get_document_summary(lang, celex_id):
    """
    Function extracts the summary of the Celex document

    Args:
        lang (string): Language of the summary that needs to be extracted
        document_page (string): Summary HTML page of the document

    Returns:
        dictionary: Summary content of the document in the provided language
    """
    summary_dict = {}
    
    # Preparing URL for the summary of the Celex number
    document_url = f'https://eur-lex.europa.eu/legal-content/{lang}/LSU/?uri=CELEX:{celex_id}'
    document_request = requests.get(document_url, timeout=10)

    if 'No legislative summaries' in document_request.text:
        summary_dict['summaryContent'] = 'NA'
        summary_dict['rawSummary'] = 'NA'
    else:
        # HTML for that information
        document_page = BeautifulSoup(document_request.text, "html.parser")
    
        language_id = f'format_language_table_HTML_{lang}'
        list_of_documents = document_page.find( 'a', attrs={'id':language_id, 'class': 'piwik_download'}, href = True)
    
        if list_of_documents is None:
            summary_dict['summaryContent'] = 'NA'
            summary_dict['rawSummary'] = 'NA'
        else:
            summary_url = 'https://eur-lex.europa.eu/'+ list_of_documents['href'][list_of_documents['href'].find("legal-content"):]
            summary_html = requests.get(summary_url).text
            summary_dict['rawSummary'] = summary_html
            summary_dict['summaryContent']= BeautifulSoup(summary_html, "html.parser").text

    return summary_dict