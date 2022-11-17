from extractors.libraries import *
from extractors import *

#####################################################################################################
# Directory Creation
# For logging the progress of the script and the list of Celex Numbers extracted
#####################################################################################################
working_dir = os.getcwd()   
directory = os.path.join(working_dir, 'Scraped_Data_Information')

if not os.path.exists(directory):
    os.makedirs(directory)

# Preparing a File to Log the Metadata Informaiton
extraction_logs = os.path.join(directory, 'Logs_Extracting_MetaData.log')

# Configuring the File name to logging Level
logging.basicConfig(filename=extraction_logs,format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO, 
                    datefmt='%d-%b-%y %H:%M:%S')

list_celex_number = pd.DataFrame(data=None)

start_time = time()
logging.info("Current date and time: " + str(start_time))

# OpenSearch Index
index_name = 'eur-lex-multilingual'

# OpenSearch Connection Setting
user_name = os.environ.get('UNI_USER')
password = os.environ.get('UNI_PWD')
es = OpenSearch(hosts = [{'host': 'Your Elastic Search Address', 'port': 443}], 
                http_auth =(user_name, password), 
                use_ssl = True,
                verify_certs = True,
                ssl_assert_hostname = False,
                ssl_show_warn = False
                )

es_index_mapping = elastic_search_mapping()
elastic_search_create(es, index_name, es_index_mapping)

# URL of the Domain specific Legal Acts, for example: Energy, Agriculture, Taxation, and other
for domain_no in range(20, 0, -1):
    print(f'Domain => {domain_no}')
    if domain_no < 10:
        domain = '0' + str(domain_no)
    else:
        domain = str(domain_no)

    provided_url = 'https://eur-lex.europa.eu/search.html?name=browse-by%3Alegislation-in-force&type=named&displayProfile=allRelAllConsDocProfile&qid=1651004540876&CC_1_CODED=' + domain

    for year in range(2022, 1950, -1):
        print('################')
        print(f'Year => {year}')

        provided_url_year = provided_url + '&DD_YEAR=' + str(year)
        # Calling the Function for the given CELEX_Numbers
        list_celex_number = celex_main(provided_url_year)
        non_existing_celex_number = elastic_search_existing_check(es, index_name, list_celex_number)

        # Calling the Function to extract the metadata for the list of celex numbers
        get_document_information(es, index_name, non_existing_celex_number)

end_time = time()
logging.info("Current date and time: " + str(end_time))
logging.info("Time for Execution of Script: " + str(end_time - start_time))