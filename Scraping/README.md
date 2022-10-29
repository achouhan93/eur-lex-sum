# **Eur-Lex-Sum Scrapper**
The project aims at extracting the metadata information from the Eur-Lex website for a respective Legal document along with the content of the document and storing it in an Elastic Search index.

## **Setting up the environment for the project**
For the python script to execute successfully **requirements.txt** file must be considered.
Locate the **requirements.txt** file and execute the below command to setup the environment for the project:
```
pip install -r requirements.txt
```

## **Execution of the project**
Execute below command to execute the project:
```
python3 eurlex_sum_extraction_main.py
```

After execution of above command, four questions will be prompted to the User:

**Question 1. Provide the URL of the Domain specific Legal Acts that needs to be extracted, for example: Energy, Agriculture, Taxation, and many more**
For Example:
1. From Legal Acts: https://eur-lex.europa.eu/browse/directories/legislation.html
2. If Legal Acts for Energy Domain is required
3. Provided URL will be: https://eur-lex.europa.eu/search.html?type=named&name=browse-by:legislation-in-force&CC_1_CODED=12&displayProfile=allRelAllConsDocProfile
```
Provide the URL: 
```

## **Elastic Search Index Mapping Information**

Following are the Document Content Information:
