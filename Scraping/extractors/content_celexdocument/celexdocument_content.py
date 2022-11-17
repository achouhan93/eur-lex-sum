from extractors.libraries import *

def get_file_by_id(lang, celex_id):
    """
    Extract the content present in the Celex document

    Args:
        lang (list): List of Celex document content language
        celex_id (string): Celex ID whose content needs to be extracted
    
    Returns:
        dictionary: Content of the document from HTML or PDF document
    """

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
        HTML_content = requests.get(url_HTML, timeout=10).text
        if 'The requested document does not exist.' in HTML_content:
            pass
            # If there is no HTML available, then try to get PDF info.
            pdf_info = requests.get(url_PDF, timeout=10)
        
            if 'The requested document does not exist.' in pdf_info.text:
                # If PDF is also not available , then Raise Exception.
                raise Exception
            
            document = "NA"
            track_dict[lang] = "PDF"

            # Save the PDF document
            working_dir = os.getcwd()
            directory = os.path.join(working_dir, 'Scraped_Data_Information')
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
        else:
            # Saving HTML File (if available)
            if "docHtml" in HTML_content:
                HTML_text = BeautifulSoup(HTML_content, "html.parser").find("div", {"id": "docHtml"})
                document_content = HTML_text.text
                document = HTML_content
            else:
                HTML_text = BeautifulSoup(HTML_content, "html.parser")
                document_content = HTML_text.text
                document = HTML_content
            
            track_dict[lang] = "HTML"

        dict['rawDocument'] = document
        dict['documentContent'] = document_content

    except :
        track_dict[lang] = "NONE"
        dict['rawDocument'] = "NA"
        dict['documentContent'] = "NA"
    
    dict['document_format'] = track_dict[lang]
    logging.info(track_dict)

    return dict