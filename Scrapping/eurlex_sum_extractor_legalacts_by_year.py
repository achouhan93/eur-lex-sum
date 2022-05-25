#!/usr/bin/env python
# coding: utf-8

# In[1]:


#################################################################################
# Extraction of the Summary for Legal Acts from Eur-lex website and 
# store it in OpenSearch (UniHeidelberg)
# 
# The Script will:
# 1. Extract the list of Celex Numbers present in different legal act domains
# 2. Extract the document content and the summary content for 24 languages present.
#################################################################################


# In[2]:


# Importing Libraries
import os
import re
import pandas as pd
from time import sleep, time

import logging

# Libraries to deal with Web Scrapping
import urllib.request
import requests
from bs4 import BeautifulSoup

# For Uni Heidelberg Server
from opensearchpy import OpenSearch
from tqdm import tqdm

import PyPDF2

# ### Celex Number Extraction

# In[3]:


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
    input_url = urllib.request.urlopen(provided_url)
    input_soup = BeautifulSoup(input_url , 'html.parser')
    page_number_indexes = input_soup.find_all('a', class_ = 'btn btn-primary btn-sm')
    if len(page_number_indexes) == 0:
        last_page_number = 2
    else:
        last_page_number_url = page_number_indexes[1].attrs['href']
        last_page_number = int((re.search('page=(\d+)', last_page_number_url , re.IGNORECASE)).group(1)) + 1
    return last_page_number


# In[4]:


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
        url = urllib.request.urlopen(provided_url + '&page=' +str(i)).read()

        # Scrapping the Page using the BeautifulSoup Library
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


# In[5]:


def celex_main(provided_url):
    """
    Orchestrator function to extract the list of Celex Numbers from the provided URL

    Args:
        provided_url (string): URL of the Domain specific Legal Acts, for example: Energy, Agriculture, Taxation, and other
                                Legal Acts: https://eur-lex.europa.eu/browse/directories/legislation.html
                                Energy Legal Acts: https://eur-lex.europa.eu/search.html?type=named&name=browse-by:legislation-in-force&CC_1_CODED=12&displayProfile=allRelAllConsDocProfile

    Returns:
        list: List of Celex numbers extracted from the provided URL
    """
    logging.info("Execution of Extraction of Celex Number - Started")

    last_page_number = pages_extraction(provided_url)
    all_celex_number = get_celex(last_page_number, provided_url)
    
    logging.info("Execution of Extraction of Celex Number - Ended")
    return all_celex_number


# ### Document Information Extraction

# In[6]:


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
    document_request = requests.get(document_url)

    if 'No legislative summaries' in document_request.text:
        summary_dict['summaryContent'] = 'NA'
    else:
        # HTML for that information
        document_page = BeautifulSoup(document_request.text, "html.parser")
    
        language_id = f'format_language_table_HTML_{lang}'
        list_of_documents = document_page.find( 'a', attrs={'id':language_id, 'class': 'piwik_download'}, href = True)
    
        if list_of_documents is None:
            summary_dict['summaryContent'] = 'NA'
        else:
            summary_url = 'https://eur-lex.europa.eu/'+ list_of_documents['href'][list_of_documents['href'].find("legal-content"):]
            summary_html = requests.get(summary_url).text
            summary_dict['summaryContent']= BeautifulSoup(summary_html, "html.parser").text

    return summary_dict


# In[ ]:


#####################################################################################################
# Function to Extract the document content for the celex document
#####################################################################################################

def get_file_by_id(lang, celex_id):
    # """"""""""
    # Functionality: Extract the content present in the Celex document
    #
    # Signature of the function:
    #  Input: 
    #       lang: List of Celex document content language
    #       celex_id: Celex Number whose content needs to be extracted
    # 
    #  Output:
    #       dict: Content of the document from HTML or PDF document
    # """""""""" 

    # Dictonary to save info for each iteration
    dict = {}

    # Tracking dictonary which type of document (HTML / PDF / NONE) in respective language
    track_dict = {}
    track_dict['celex_id'] = celex_id  

########################################################################################################
    # Preparing URLs based on given number & Language.
    url_HTML = f'https://eur-lex.europa.eu/legal-content/{lang}/TXT/HTML/?uri=CELEX:{celex_id}'
    url_PDF = f'https://eur-lex.europa.eu/legal-content/{lang}/TXT/PDF/?uri=CELEX:{celex_id}'
########################################################################################################
    try:
        # First try to get HTML information
        HTML_content = requests.get(url_HTML).text
        if 'The requested document does not exist.' in HTML_content:
            pass
            # If there is no HTML available, then try to get PDF info.
            pdf_info = requests.get(url_PDF)
        
            if 'The requested document does not exist.' in pdf_info.text:
                # If PDF is also not available , then Raise Exception.
                raise Exception

            # Save the PDF document
            working_dir = os.getcwd()
            directory = os.path.join(working_dir, 'Scrapped_Data_Information')
            if not os.path.exists(directory):
                os.makedirs(directory)
            
            pdf_directory = os.path.join(directory, 'PDF_Documents')
            if not os.path.exists(pdf_directory):
                os.makedirs(pdf_directory)

            pdf_document_path = os.path.join(pdf_directory, celex_id + "_" + lang + ".pdf" )

            save_pdf = open(pdf_document_path, 'wb')
            save_pdf.write(pdf_info.content)
            save_pdf.close()

            read_pdf = PyPDF2.PdfFileReader(pdf_document_path, strict=False)

            all_pages = {}
            num = read_pdf.getNumPages()
            for page in range(num):
                data = read_pdf.getPage(page)

                # extract the page's text
                page_text = data.extractText()

                # put the text data into the dict
                all_pages[page] = page_text
            
            content = ''
            for page in all_pages:
                content = content + '[NEW PAGE] ' + all_pages[page] 
            
            document_content = content
            track_dict[lang] = "PDF"
        else:
            # Saving HTML File (if available)
            if "docHtml" in HTML_content:
                HTML_text = BeautifulSoup(HTML_content, "html.parser").find("div", {"id": "docHtml"})
                document_content = HTML_text.text
            else:
                HTML_text = BeautifulSoup(HTML_content, "html.parser")
                document_content = HTML_text.text
            
            track_dict[lang] = "HTML"

        dict['documentContent'] = document_content

    except :
        track_dict[lang] = "NONE"
        dict['documentContent'] = "NA"
    
    logging.info(track_dict)

    return dict


# In[7]:


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
            summary_data = get_document_summary(lang, celex_id)
            document_information = get_file_by_id(lang, celex_id)
                
            language_document_information['documentInformation'] = document_information
            language_document_information['summaryInformation'] = summary_data
            celex_document_information[lang] = language_document_information

            logging.info(f'Completed Extracting Information of {celex_id} for {lang}')
            sleep(1)       
        
        elastic_search_insert(es, index_name, celex_document_information)
        logging.info("Execution of Extraction of Summary for respective Celex Document - Ended")


# In[8]:


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
                "bulgarian": {
                    "type": "nested",
                    "properties": {
                        "documentInformation": {
                            "type": "nested",
                            "properties": {
                                "documentContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                },
                                "summaryContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                },
                "spanish": {
                    "type": "nested",
                    "properties": {
                        "documentInformation": {
                            "type": "nested",
                            "properties": {
                                "documentContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                },
                                "summaryContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                },
                "czech": {
                    "type": "nested",
                    "properties": {
                        "documentInformation": {
                            "type": "nested",
                            "properties": {
                                "documentContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                },
                                "summaryContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                },
                "danish": {
                    "type": "nested",
                    "properties": {
                        "documentInformation": {
                            "type": "nested",
                            "properties": {
                                "documentContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                },
                                "summaryContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                },
                "german": {
                    "type": "nested",
                    "properties": {
                        "documentInformation": {
                            "type": "nested",
                            "properties": {
                                "documentContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                },
                                "summaryContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                },
                "estonian": {
                    "type": "nested",
                    "properties": {
                        "documentInformation": {
                            "type": "nested",
                            "properties": {
                                "documentContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                },
                                "summaryContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                },
                "greek": {
                    "type": "nested",
                    "properties": {
                        "documentInformation": {
                            "type": "nested",
                            "properties": {
                                "documentContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                },
                                "summaryContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                },
                "english": {
                    "type": "nested",
                    "properties": {
                        "documentInformation": {
                            "type": "nested",
                            "properties": {
                                "documentContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                },
                                "summaryContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                },
                "french": {
                    "type": "nested",
                    "properties": {
                        "documentInformation": {
                            "type": "nested",
                            "properties": {
                                "documentContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                },
                                "summaryContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                },
                "irish": {
                    "type": "nested",
                    "properties": {
                        "documentInformation": {
                            "type": "nested",
                            "properties": {
                                "documentContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                },
                                "summaryContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                },
                "croatian": {
                    "type": "nested",
                    "properties": {
                        "documentInformation": {
                            "type": "nested",
                            "properties": {
                                "documentContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                },
                                "summaryContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                },
                "italian": {
                    "type": "nested",
                    "properties": {
                        "documentInformation": {
                            "type": "nested",
                            "properties": {
                                "documentContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                },
                                "summaryContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                },
                "latvian": {
                    "type": "nested",
                    "properties": {
                        "documentInformation": {
                            "type": "nested",
                            "properties": {
                                "documentContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                },
                                "summaryContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                },
                "lithuanian": {
                    "type": "nested",
                    "properties": {
                        "documentInformation": {
                            "type": "nested",
                            "properties": {
                                "documentContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                },
                                "summaryContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                },
                "hungarian": {
                    "type": "nested",
                    "properties": {
                        "documentInformation": {
                            "type": "nested",
                            "properties": {
                                "documentContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                },
                                "summaryContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                },
                "maltese": {
                    "type": "nested",
                    "properties": {
                        "documentInformation": {
                            "type": "nested",
                            "properties": {
                                "documentContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                },
                                "summaryContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                },
                "dutch": {
                    "type": "nested",
                    "properties": {
                        "documentInformation": {
                            "type": "nested",
                            "properties": {
                                "documentContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                },
                                "summaryContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                },
                "polish": {
                    "type": "nested",
                    "properties": {
                        "documentInformation": {
                            "type": "nested",
                            "properties": {
                                "documentContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                },
                                "summaryContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                },
                "portuguese": {
                    "type": "nested",
                    "properties": {
                        "documentInformation": {
                            "type": "nested",
                            "properties": {
                                "documentContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                },
                                "summaryContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                },
                "romanian": {
                    "type": "nested",
                    "properties": {
                        "documentInformation": {
                            "type": "nested",
                            "properties": {
                                "documentContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                },
                                "summaryContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                },
                "slovak": {
                    "type": "nested",
                    "properties": {
                        "documentInformation": {
                            "type": "nested",
                            "properties": {
                                "documentContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                },
                                "summaryContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                },
                "slovenian": {
                    "type": "nested",
                    "properties": {
                        "documentInformation": {
                            "type": "nested",
                            "properties": {
                                "documentContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                },
                                "summaryContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                },
                "finnish": {
                    "type": "nested",
                    "properties": {
                        "documentInformation": {
                            "type": "nested",
                            "properties": {
                                "documentContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                },
                                "summaryContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                },
                "swedish": {
                    "type": "nested",
                    "properties": {
                        "documentInformation": {
                            "type": "nested",
                            "properties": {
                                "documentContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                },
                                "summaryContent": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    return es_mapping


# In[9]:


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


# In[10]:


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
    doc = { 
            "bulgarian":
            {
                "documentInformation":
                    {
                        "documentContent":celex_information['BG']['documentInformation']['documentContent'],
                        "summaryContent":celex_information['BG']['summaryInformation']['summaryContent']
                    }
            },
            "spanish":
            {
                "documentInformation":
                    {
                        "documentContent":celex_information['ES']['documentInformation']['documentContent'],
                        "summaryContent":celex_information['ES']['summaryInformation']['summaryContent']
                    }
            },
            "czech":
            {
                "documentInformation":
                    {
                        "documentContent":celex_information['CS']['documentInformation']['documentContent'],
                        "summaryContent":celex_information['CS']['summaryInformation']['summaryContent']
                    }
            },
            "danish":
            {
                "documentInformation":
                    {
                        "documentContent":celex_information['DA']['documentInformation']['documentContent'],
                        "summaryContent":celex_information['DA']['summaryInformation']['summaryContent']
                    }
            },
            "german":
            {
                "documentInformation":
                    {
                        "documentContent":celex_information['DE']['documentInformation']['documentContent'],
                        "summaryContent":celex_information['DE']['summaryInformation']['summaryContent']
                    }
            },
            "estonian":
            {
                "documentInformation":
                    {
                        "documentContent":celex_information['ET']['documentInformation']['documentContent'],
                        "summaryContent":celex_information['ET']['summaryInformation']['summaryContent']
                    }
            },
            "greek":
            {
                "documentInformation":
                    {
                        "documentContent":celex_information['EL']['documentInformation']['documentContent'],
                        "summaryContent":celex_information['EL']['summaryInformation']['summaryContent']
                    }
            },
            "english":
            {
                "documentInformation":
                    {
                        "documentContent":celex_information['EN']['documentInformation']['documentContent'],
                        "summaryContent":celex_information['EN']['summaryInformation']['summaryContent']
                    }
            },
            "french":
            {
                "documentInformation":
                    {
                        "documentContent":celex_information['FR']['documentInformation']['documentContent'],
                        "summaryContent":celex_information['FR']['summaryInformation']['summaryContent']
                    }
            },
            "irish":
            {
                "documentInformation":
                    {
                        "documentContent":celex_information['GA']['documentInformation']['documentContent'],
                        "summaryContent":celex_information['GA']['summaryInformation']['summaryContent']
                    }
            },
            "croatian":
            {
                "documentInformation":
                    {
                        "documentContent":celex_information['HR']['documentInformation']['documentContent'],
                        "summaryContent":celex_information['HR']['summaryInformation']['summaryContent']
                    }
            },
            "italian":
            {
                "documentInformation":
                    {
                        "documentContent":celex_information['IT']['documentInformation']['documentContent'],
                        "summaryContent":celex_information['IT']['summaryInformation']['summaryContent']
                    }
            },
            "latvian":
            {
                "documentInformation":
                    {
                        "documentContent":celex_information['LV']['documentInformation']['documentContent'],
                        "summaryContent":celex_information['LV']['summaryInformation']['summaryContent']
                    }
            },
            "lithuanian":
            {
                "documentInformation":
                    {
                        "documentContent":celex_information['LT']['documentInformation']['documentContent'],
                        "summaryContent":celex_information['LT']['summaryInformation']['summaryContent']
                    }
            },
            "hungarian":
            { 
                "documentInformation":
                    {
                        "documentContent":celex_information['HU']['documentInformation']['documentContent'],
                        "summaryContent":celex_information['HU']['summaryInformation']['summaryContent']
                    }
            },
            "maltese":
            {
                "documentInformation":
                    {
                        "documentContent":celex_information['MT']['documentInformation']['documentContent'],
                        "summaryContent":celex_information['MT']['summaryInformation']['summaryContent']
                    }
            },
            "dutch":
            {
                "documentInformation":
                    {
                        "documentContent":celex_information['NL']['documentInformation']['documentContent'],
                        "summaryContent":celex_information['NL']['summaryInformation']['summaryContent']
                    }
            },
            "polish":
            {
                "documentInformation":
                    {
                        "documentContent":celex_information['PL']['documentInformation']['documentContent'],
                        "summaryContent":celex_information['PL']['summaryInformation']['summaryContent']
                    }
            },
            "portuguese":
            {
                "documentInformation":
                    {
                        "documentContent":celex_information['PT']['documentInformation']['documentContent'],
                        "summaryContent":celex_information['PT']['summaryInformation']['summaryContent']
                    }
            },
            "romanian":
            {
                "documentInformation":
                    {
                        "documentContent":celex_information['RO']['documentInformation']['documentContent'],
                        "summaryContent":celex_information['RO']['summaryInformation']['summaryContent']
                    }
            },
            "slovak":
            {
                "documentInformation":
                    {
                        "documentContent":celex_information['SK']['documentInformation']['documentContent'],
                        "summaryContent":celex_information['SK']['summaryInformation']['summaryContent']
                    }
            },
            "slovenian":
            {
                "documentInformation":
                    {
                        "documentContent":celex_information['SL']['documentInformation']['documentContent'],
                        "summaryContent":celex_information['SL']['summaryInformation']['summaryContent']
                    }
            },
            "finnish":
            {
                "documentInformation":
                    {
                        "documentContent":celex_information['FI']['documentInformation']['documentContent'],
                        "summaryContent":celex_information['FI']['summaryInformation']['summaryContent']
                    }
            },
            "swedish":
            {
                "documentInformation":
                    {
                        "documentContent":celex_information['SV']['documentInformation']['documentContent'],
                        "summaryContent":celex_information['SV']['summaryInformation']['summaryContent']
                    }
            }
        }
    _id = celex_information['_id']
    
    try:
        es_index.index(index=index_name,body=doc,id=_id)
    except Exception as e:
        logging.error('Indexing celex id \'{}\' failed to push in OpenSearch'.format(_id))


# In[11]:


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


# In[13]:


if __name__ == '__main__':

    #####################################################################################################
    # Directory Creation
    # For logging the progress of the script and the list of Celex Numbers extracted
    #####################################################################################################
    working_dir = os.getcwd()   
    directory = os.path.join(working_dir, 'Scrapped_Data_Information')

    if not os.path.exists(directory):
        os.makedirs(directory)

    # Preparing a File to Log the Metadata Informaiton
    extraction_logs = os.path.join(directory, 'Logs_Extracting_MetaData.log')
    
    # Configuring the File name to logging Level
    logging.basicConfig(filename=extraction_logs,format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO, datefmt='%d-%b-%y %H:%M:%S')

    list_celex_number = pd.DataFrame(data=None)

    start_time = time()
    logging.info("Current date and time: " + str(start_time))

    # OpenSearch Index
    index_name = 'eur-lex-multilingual'

    # OpenSearch Connection Setting
    user_name = os.environ.get('UNI_USER')
    password = os.environ.get('UNI_PWD')
    es = OpenSearch(hosts = [{'host': 'elastic-dbs.ifi.uni-heidelberg.de', 'port': 443}], 
    http_auth =(user_name, password), 
    use_ssl = True,
    verify_certs = True,
    ssl_assert_hostname = False,
    ssl_show_warn = False
    )

    es_index_mapping = elastic_search_mapping()
    elastic_search_create(es, index_name, es_index_mapping)
    
    # URL of the Domain specific Legal Acts, for example: Energy, Agriculture, Taxation, and other
    for year in range(2022, 1950, -1):
        print('################')
        print(f'Year => {year}')
        for domain_no in range(1, 21):
            if domain_no < 10:
                domain = '0' + str(domain_no)
            else:
                domain = str(domain_no)
            
            print(f'Domain => {domain_no}')
            provided_url = 'https://eur-lex.europa.eu/search.html?name=browse-by%3Alegislation-in-force&type=named&displayProfile=allRelAllConsDocProfile&qid=1651004540876&CC_1_CODED=' + domain

            provided_url_year = provided_url + '&DD_YEAR=' + str(year)
            # Calling the Function for the given CELEX_Numbers
            list_celex_number = celex_main(provided_url_year)
            non_existing_celex_number = elastic_search_existing_check(es, index_name, list_celex_number)

            # Calling the Function to extract the metadata for the list of celex numbers
            get_document_information(es, index_name, non_existing_celex_number)

    end_time = time()
    logging.info("Current date and time: " + str(end_time))
    logging.info("Time for Execution of Script: " + str(end_time - start_time))

