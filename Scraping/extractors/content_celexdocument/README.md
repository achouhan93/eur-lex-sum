## **content_celexdocument**
The scripts in the folder are microservices that aim to extract the document and summary content for a celex id in the respective language.

### Explanation

#### `celexdocument_content.py`
The goal of the script is to extract the `document content` for the celex id in the respective language. The script will first check for the document content in the `HTML format`; if the HTML format is not present, the script will look for the document content in PDF format. Furthermore, if the document content is neither in HTML nor PDF, the script returns `NA` as the document content.

#### `celexdocument_summary.py`
The goal of the script is to extract the `summary content` for the celex id in the respective language. The script will first check for the summary content in the `HTML format`; if the HTML format is not present, the script will look for the summary content in PDF format. Furthermore, if the summary content is neither in HTML nor PDF, the script returns `NA` as the summary content.