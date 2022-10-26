# **LeXtractor**
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
python3 master_alphaextraction.py
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

**Question 2. Provide the name of the Elastic Search index that needs to be considered for putting the extracted information**
For Example: eur-lex
```
Provide the Elastic Search Index Name: 
``` 

**Question 3. Provide the Elastic Search server information**
Possible answers to this questions are:
1. localhost
2. Uniheidelberg

If the Elastic Search on local system needs to be considered then **localhost** needs to be entered.

If the Elastic Search executing on University Heidelberg server needs to be considered then **Uniheidelberg** needs to be entered.
```
Server of the Elastic Search Index (localhost or Uniheidelberg): 
```

**Question 4. Celex document of how many pages needs to be considered from the provided URL**
Number of pages value must be less than or equal to total number of pages present in the provided URL.
```
Number of Pages that needs to be considered for Document Extraction: 
```

Once all the questions are answered, the script will start extracting the metadata information from the Eur-Lex website along with the content present in the legal document and store it in Elastic Search index.

## **Elastic Search Index Mapping Information**
A total of 34 metadata information for a specific legal document will be extracted from the Eur-Lex website.
Following are the Metadata Information that are extracted:

    * title
    * ELI_LINK
    * Date of document
    * Date of effect
    * Date of signature
    * Deadline
    * Date of end of validity
    * EUROVOC descriptor
    * Subject matter
    * Directory code
    * Author
    * Form
    * Additional Information
    * Procedure number
    * Link
    * Treaty
    * Legal basis
    * Proposal
    * Amended by
    * All consolidate versions
    * Instruments cited
    * Authentic language
    * Addressee
    * Date of notification
    * Responsible body
    * Related documents
    * Internal comment
    * Affected by case
    * Subsequent related instruments
    * Internal reference
    * Date of transposition
    * Depositary
    * Internal procedures based on this legislative basic act
    * Co-author

Following are the Document Content Information:

    * Document Format
    * Document Language
    * Raw document
    * Content_EN