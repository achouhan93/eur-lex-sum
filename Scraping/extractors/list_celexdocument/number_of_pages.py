from extractors.libraries import *

def pages_extraction(provided_url):
    """
    Function extracts the number of pages that needs to be considered for extracting the Celex Numbers

    Args:
        provided_url (string): URL of the Domain specific Legal Acts, for example: Energy, Agriculture, Taxation, and others
                                Legal Acts: https://eur-lex.europa.eu/browse/directories/legislation.html
                                Energy Legal Acts: https://eur-lex.europa.eu/search.html?type=named&name=browse-by:legislation-in-force&CC_1_CODED=12&displayProfile=allRelAllConsDocProfile

    Returns:
        integer: Value of the number of pages present in the provided URL
    """
    input_url = urllib.request.urlopen(provided_url, timeout=10)
    input_soup = BeautifulSoup(input_url , 'lxml')
    page_number_indexes = input_soup.find_all('a', class_ = 'btn btn-primary btn-sm')
    if len(page_number_indexes) == 0:
        last_page_number = 2
    else:
        last_page_number_url = page_number_indexes[1].attrs['href']
        last_page_number = int((re.search('page=(\d+)', last_page_number_url , re.IGNORECASE)).group(1)) + 1
    return last_page_number