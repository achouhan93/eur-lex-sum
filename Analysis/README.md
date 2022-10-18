## Download the data file
For the analysis, we mostly use an offline version of our dataset.
You can download the `.pkl` file containing all filtered samples from here:
https://heibox.uni-heidelberg.de/f/f7ac20161b8e433dacee/

Alternatively, we recommend using the final version of our dataset through Huggingface:
https://huggingface.co/datasets/dennlinger/eur-lex-sum

## Explanation

### `Insights/`
This folder contains resulting figures and files containing evaluation scores.
Finally, some files contain a subset of Celex IDs, which satisfy some of the filtering criteria,
with respect to the single-/multi-reference issue.

### `unused_scripts/`
Contains a number of scripts that were used during the analysis, but are no longer required
to reproduce any of results in the paper.

### `config.py` (Private)
To access our internal Opensearch index, we are using a private username and password.
Should you want to reproduce results from the original corpus (and not the filtered offline version),
please reach out to us to discuss access options to our servers.

### `evaluate_elastic_corpus.py`
Script to analyze the data directly through elastic.
Running this requires access to our servers, but should not be required for reproducibility.

### `filter_data_for_offline_use.py`
This was used to create an offline copy of the data (with minor pre-filtering).
The main reason was simply to avoid re-accessing (slow) Elastic transfer via the web,
and instead access a local copy.
Running this requires access to our servers, but should not be required for reproducibility.

### `investigate_offline_data.py`
Generates the `clean_data.pkl` file that is available online for direct download.
Therefore, running this is not strictly required; 
however, it requires running `filter_data_for_offline_use.py` first.

This script was also used to investigate (and filter) several aspects mentioned in the paper.
As an example, samples with shorter reference texts (compared to their respective summaries) are filtered out.

### `rebuttal_additional_stats.py`
This script produces two further experiments, based on original comments by Reviewer 1.
In particular, it investigates the problem of only using a single reference for multi-referenced documents.
Secondly, it expands on the distribution of Celex IDs in multiple languages.
In short, we find that most samples are present in 20+ languages.

### `utils.py`
Contains various abstractions that are used across multiple files (potentially).
In particular, implements several filters (such as filtering PDF scans) for the dataset processing.