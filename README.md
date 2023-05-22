# EUR-Lex-Sum: A Multi- and Cross-lingual Dataset for Long-form Summarization in the Legal Domain

Dennis Aumiller*, Ashish Chouhan*, and Michael Gertz  
Heidelberg University & SRH Hochschule Heidelberg  
contact us at: [`{aumiller, chouhan, gertz}@informatik.uni-heidelberg.de`](mailto:aumiller@informatik.uni-heidelberg.de)

**Find our dataset on the Huggingface Hub:** 🤗 [eur-lex-sum](https://huggingface.co/datasets/dennlinger/eur-lex-sum)    
The data card also provides further insight on the acquisition process (and some limitations) of the data. Please refer to the Huggingface Hub for more information.  
A [pre-print](https://arxiv.org/abs/2210.13448) of our work is available; it has also been accepted at the main conference track of EMNLP 2022, conference proceedings will be available in December 2022.

## Installation
Install all necessary dependencies by running

```
python3 -m pip install -r requirements.txt
```
 after cloning this repository.

This code base provides necessary scripts for the scraping process (`Scraping/`), as well as the analysis of our corpus (`Analysis/`) and final baseline experiments (`Baselines/`).

## Comparison to Related Work

For a comparison of language-specific stats, please refer to Table 5 in our [pre-print](https://arxiv.org/abs/2210.13448).

| Dataset Name        | Domain     | Number of Languages | Average Tokens in Reference Text | Average Tokens in the Summary text (in words) | Compression Ratio | Dataset              |
| :-------------------------: | :----------: | :--------: | :--------------------------------: | :---------------------------------------------: | :-----------------: | :--------------------: |
| [EUR-Lex-Sum](https://arxiv.org/abs/2210.13448) - Our Contribution        | Legal      | 24        | 12,200 (EN)  | 799 (EN)     | 16 | [🤗](https://huggingface.co/datasets/dennlinger/eur-lex-sum) |
| [BillSum (US)](https://aclanthology.org/D19-5406/)        | Legal      | 1        | 1382                             | 2000 characters, Words are not considered as tokens     | -      | [🤗](https://huggingface.co/datasets/billsum) |
| [BillSum (CA)](https://aclanthology.org/D19-5406/)        | Legal      | 1        | 1684                             | 2000 characters, Words are not considered as tokens    | -      | [🤗](https://huggingface.co/datasets/billsum) |
| [Global Voices](https://aclanthology.org/D19-5411/)       | News       | 15       | 359                              | 51                                            | -      | [Paperswithcode](https://paperswithcode.com/dataset/global-voices)        |
| [WikiLingua](https://aclanthology.org/2020.findings-emnlp.360/)          | WikiHow    | 18       | 391                              | 39                                            | -      | [🤗](https://huggingface.co/datasets/wiki_lingua) |
| [Xwikis (comparable)](https://aclanthology.org/2021.emnlp-main.742/)      | Wikipedia  | 4        | 945                              | 77                                            | EN: ~12.2        | [🤗](https://huggingface.co/datasets/GEM/xwikis)                     |
| [Xwikis (parallel)](https://aclanthology.org/2021.emnlp-main.742/)      | Wikipedia  | 4        | 972                              | 76                                            | 18.35             | [🤗](https://huggingface.co/datasets/GEM/xwikis)                                           |
| [Spektrum (Wiki)](https://aclanthology.org/2021.newsum-1.5/)     | Wikipedia  | 2        | 1559                             | 140                                           | 20                | [![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)](https://github.com/mehwishfatimah/wsd)                    |
| [Spektrum (Spektrum)](https://aclanthology.org/2021.newsum-1.5/) | Scientific | 2        | 2337                             | 361                                           | 30                | [![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)](https://github.com/mehwishfatimah/wsd)                    |
| [CLIDSUM (Chat)](https://ui.adsabs.harvard.edu/abs/2022arXiv220205599W/abstract)      | Dialogue   | 3        | 83,9                             | 20,3                                          | -      | [![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)](https://github.com/krystalan/ClidSum)     |
| [CLIDSUM (Interview)](https://ui.adsabs.harvard.edu/abs/2022arXiv220205599W/abstract) | Dialogue   | 3        | 1555,4                           | 14,4                                          | -      | [![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)](https://github.com/krystalan/ClidSum)     |
| [MLSUM](https://aclanthology.org/2020.emnlp-main.647/)               | News       | 5        | (French) FR: 632,39                       | FR: 29,5                                      | FR: 21,4          | [🤗](https://huggingface.co/datasets/mlsum)                                         |
| | | | (German) DE: 570,6           | DE: 30,36  | DE: 18,8 |                                  |
| | | | (Spanish) ES: 800,50          | ES: 20,71  | ES: 38,7 |                                  |
| | | | (Russian) RU: 959,4           | RU: 14,57  | RU: 65,8 |                                  |
| | | | (Turkish) TU: 309,18          | TU: 22,88  | TU: 13,5 |                                  |
| | | | (English) EN: 790,24          | EN: 55,56  | EN: 14,2 |                                  |



## Cite our work
If you use the dataset or other parts of this code base, please use the following citation for attribution:

```
@inproceedings{aumiller-etal-2022-eur,
    title = {{EUR-Lex-Sum: A Multi- and Cross-lingual Dataset for Long-form Summarization in the Legal Domain}},
    author = "Aumiller, Dennis  and
      Chouhan, Ashish  and
      Gertz, Michael",
    booktitle = "Proceedings of the 2022 Conference on Empirical Methods in Natural Language Processing",
    month = dec,
    year = "2022",
    address = "Abu Dhabi, United Arab Emirates",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2022.emnlp-main.519",
    pages = "7626--7639"
}

```

## License Information
Copyright for the editorial content of EUR-Lex website, the summaries of EU legislation and the consolidated texts owned by the EU, are licensed under the [Creative Commons Attribution 4.0 International licence](https://creativecommons.org/licenses/by/4.0/), i.e., CC BY 4.0 as mentioned on the official [EUR-Lex website](https://eur-lex.europa.eu/content/legal-notice/legal-notice.html#2.%20droits).  Any data artifacts remain licensed under the CC BY 4.0 license.

## License for software component
Per recommendation of the Creative Commons, we apply a separate license to the software component of this repository. We use the standard [MIT](https://choosealicense.com/licenses/mit/) license for code artifacts.
