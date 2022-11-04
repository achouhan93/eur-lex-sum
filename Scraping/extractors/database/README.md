## **database**
The scripts in the folder are database objects that tackle the operations taking place concerning the database. In the current scenario, Elastic search is used as a database.

### Explanation

#### `database_create.py`
For the provided elastic search index name, the script will check if the index already exists. If the index is not present, it will create the index based on index mappings in `database_mapping.py`.

#### `database_insert.py`
The primary goal of this script is to insert the document in the elastic search index. The document will comprise of legislative document and summary content in `24` languages for a respective celex id.

#### `database_mapping.py`
This script comprises the elastic search index mapping.

#### `database_record_check.py`
For the extracted list of celex IDs present on the URL, the task of this script is to check if the celex id document is `already existing` in the elastic search index. The output from the script is a list of non-existing celex ids whose document and summary content needs to be extracted from the eur-lex website.