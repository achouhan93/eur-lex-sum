## **Scrapper**
The scripts in the folder aim to extract the content of the legislative document and its respective summary from [Eur-lex platform](https://eur-lex.europa.eu/browse/directories/legislation.html). After extracting the document content and summary, the information is stored in an Elastic Search index with `_id` as the celex ID of each document.

### **Execution of the project**

#### `Before execution`
Before execution of the `eurlex_sum_extraction_main.py`, i.e., the main script to start scrapping the information and storing it in Elastic Search Index. Please make sure to take the following steps:

  1. Set environment variable UNI_USER, i.e., Elastic Search Username**
  2. Set environment variable UNI_PWD, i.e., Elastic Search Password**
     ```python
     user_name = os.environ.get('UNI_USER')
     password = os.environ.get('UNI_PWD')
     ```
  3. Replace "Your Elastic Search Address" string in `eurlex_sum_extraction_main.py` with
     the address of Elastic search where the index needs to be created**
     ```python
     es = OpenSearch(hosts = [{'host': 'Your Elastic Search Address', 'port': 443}], 
                     http_auth =(user_name, password), 
                     use_ssl = True,
                     verify_certs = True,
                     ssl_assert_hostname = False,
                     ssl_show_warn = False
                     )
     ```

#### `For execution`
Execute the below command to execute the project:
```
python3 eurlex_sum_extraction_main.py
```

### Explanation of Script

#### ```eurlex_sum_extraction_main.py```
The script is the primary driver for scrapping the information from the eur-lex website and storing it in the elastic search index. The first task performed by the script is to check if the elastic search has an index by the name ```eur-lex-multilingual```. If the index is not present, then the script will create the index using the index mappings from function ```elastic_search_mapping``` present in ```extractors/database/database_mapping.py```. Once the index is created, the driver script will start scrapping the eur-lex website.

The eur-lex website for legislative documents comprises ```20``` domains, and each domain has documents published in different years from `1951 till date and still going`. Thus, the second task of the script is to create the URL for a specific domain and year used for the sequential scrapping of documents and their respective summaries. 

For Example:
1. From Legal Acts: https://eur-lex.europa.eu/browse/directories/legislation.html
2. If Legal Acts for Energy Domain are required. (`domain_number = 12`)
3. Provided URL will be: https://eur-lex.europa.eu/search.html?type=named&name=browse-by:legislation-in-force&CC_1_CODED=`domain_number`&displayProfile=allRelAllConsDocProfile

Once the URL is created, the script extracts the `celex id` of the document present on the URL by calling the function `celex_main` from `extractors/celexdocument_list.py`. The script will also check for the document if it already exists using celex id in the elastic search index by calling the function `elastic_search_existing_check` from `extractors/database/database_record_check.py`. If the document is in the elastic search index, the script will ignore the document for further scrapping the information.

After checking the document exists in the elastic search index, a list of non-existing celex id is provided to extract the document and summary content from the website and store it in elastic search by calling the function `get_document_information` from `extractors/celexdocument_information.py`.

Every step of the script will be logged in a log file by the name `Logs_Extracting_MetaData.log` present in the folder `Scrapped_Data_Information`. If the file and folder are not present, then the script will create the folder and file.