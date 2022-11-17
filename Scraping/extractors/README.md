## **extractors**
The scripts in the folder are microservices that aim to perform a specific task. Every script comprises functions that have a specific signature.

### Explanation

#### `content_celexdocument/`
The task of the scripts present in this `folder` is to extract the legislative document content and their respective summaries.

### `database/`
The scripts present in this `folder` are database objects. Task-specific to database (elastic search) operations are present in this folder. The operations include the creation of the index, mappings required to create the index, inserting documents in the index, and checking the existence of the documents in the index.

### `list_celexdocument/`
The task of the scripts present in this `folder` is to gather the list of celex ids of the legislative document present on the URL for a specific domain and year.

#### `celexdocument_information.py`
The script is the primary driver for gathering the document and summary content from the eur-lex website for a respective celex id in `24` languages. For a respective celex id and language, the `get_document_summary` function is executed from `content_celexdocument/celexdocument_summary.py` to extract the summary of the document. The `get_file_by_id` function is executed from `content_celexdocument/celexdocument_information.py` to extract the document content. A dictionary is created for a celex id, where each language has a document and summary content is present. This dictionary is then passed to the function `elastic_search_insert` from `database/database_insert.py` to insert the information for a specific celex id in the elastic search index.

#### `celexdocument_list.py`
The task of this script is to provide a list of celex IDs in the URL by tackling the pagination on the web page. At a given point in time, the web page only displays a `10` document. Suppose a URL has `80` documents; then `8` pages will be present, having `10` documents on each page. Thus, the script will browse over all the pages and extract the celex id present on those pages.

#### `libraries.py`
The script comprises all the import statements of the libraries required to execute the scraper.