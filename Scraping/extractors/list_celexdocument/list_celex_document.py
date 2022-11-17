from extractors.libraries import *

def get_celex(pages, provided_url):
    """
    Function extracts all the Celex Number of the documents from the considered URL

    Args:
        pages (integer): The value of number of pages that needs to be considered for extracting the Celex Numbers
        provided_url (string): URL of the Domain specific Legal Acts, for example: Energy, Agriculture, Taxation, and other
                                Legal Acts: https://eur-lex.europa.eu/browse/directories/legislation.html
                                Energy Legal Acts: https://eur-lex.europa.eu/search.html?type=named&name=browse-by:legislation-in-force&CC_1_CODED=12&displayProfile=allRelAllConsDocProfile

    Returns:
        list: List of Celex Number extracted from the provided URL
    """    
    list_celex = []
    
    # Looping over all the pages present for the legal act
    for i in range(1, pages):
        # URL is create for each page of the legal act domain
        sleep(1)
        url = urllib.request.urlopen(provided_url + '&page=' +str(i), timeout=10).read()

        # Scraping the Page using the BeautifulSoup Library
        soup = BeautifulSoup(url , 'lxml')

        # Fetching celex numbers by parsing html tags heirarchy and checking for text 'CELEX number' 
        try:
            div_tags = soup.find_all("div", attrs={"class": "col-sm-6"})
            for tag in div_tags:
                titles = tag.find_all("dt")
                values = tag.find_all("dd")
                for t ,v in zip(titles, values):
                    if t.text == 'CELEX number: ':
                        list_celex.append(v.text)
        except:
            pass

    return list_celex