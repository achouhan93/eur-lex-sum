## **Scraper**
The scripts in this folder aim to extract the content of a legislative document and its respective summary from the [EUR-Lex platform](https://eur-lex.europa.eu/browse/directories/legislation.html). After extracting the document content and summary, the information is stored in an Elastic Search index with the document's Celex ID serving as the unique `_id` in the Elastic index.

### **Execution of the project**
Note that this project is tailored to the compute infrastructure at the institute of the authors; for reproducibility, you will have to adjust the respective URL addresses and user names to work with your local environment.

#### Before execution
Before executing `eurlex_sum_extraction_main.py`, the main entrypoint for the scraper, please make sure to complete the following steps:

  1. Set the required environment variable `UNI_USER`, which should set the username used for Elasticsearch
  2. In accordance, set the environment variable `UNI_PWD` to the Elastic password; they respective code retrieving said variables is shown below.
     ```python
     user_name = os.environ.get('UNI_USER')
     password = os.environ.get('UNI_PWD')
     ```
  3. Replace "Your Elastic Search Address" string in `eurlex_sum_extraction_main.py` with
     the address of Elasticsearch in your local network.
     ```python
     es = OpenSearch(hosts = [{'host': 'Your Elastic Search Address', 'port': 443}], 
                     http_auth =(user_name, password), 
                     use_ssl = True,
                     verify_certs = True,
                     ssl_assert_hostname = False,
                     ssl_show_warn = False
                     )
     ```

#### Start the Scraper
Once everything is set up, start the scraper by running
```
python3 eurlex_sum_extraction_main.py
```

### Explanation

#### ```eurlex_sum_extraction_main.py```
The script is the primary driver for scraping the information from the eur-lex website and storing it in the elastic search index. The first task performed by the script is to check if the elastic search has an index by the name ```eur-lex-multilingual```. If the index is not present, then the script will create the index using the index mappings from function ```elastic_search_mapping``` present in ```extractors/database/database_mapping.py```. Once the index is created, the driver script will start scraping the eur-lex website.

The eur-lex website for legislative documents comprises 20 domains, and each domain has documents published in different years from 1951 onwards. Thus, the second task of the script is to create the URL for a specific domain and year used for the sequential scraping of documents and their respective summaries. 

For Example:
1. From Legal Acts: https://eur-lex.europa.eu/browse/directories/legislation.html
2. If Legal Acts for Energy Domain are required. (`domain_number = 12`)
3. Provided URL will be: https://eur-lex.europa.eu/search.html?type=named&name=browse-by:legislation-in-force&CC_1_CODED=`domain_number`&displayProfile=allRelAllConsDocProfile

Note that the list of obtainable URLs might change in the future, and is therefore not necessarily equivalent to the presented corpus in this work.  
Once the URL is created, the script extracts the Celex id of the document present on the URL by calling the function `celex_main` from `extractors/celexdocument_list.py`. The script will also check for the document if it already exists using the Celex id as a search call to Elastic, using the function `elastic_search_existing_check` from `extractors/database/database_record_check.py`. If the document is in the elastic search index, the script will ignore the document for further scraping the information.

After checking the document exists in the elastic search index, a list of non-existing celex id is provided to extract the document and summary content from the website and store it in elastic search by calling the function `get_document_information` from `extractors/celexdocument_information.py`.

Every step of the script will be logged in a log file by the name `Logs_Extracting_MetaData.log` present in the folder `Scraped_Data_Information`. If the file and folder are not present, then the script will create the folder and file.