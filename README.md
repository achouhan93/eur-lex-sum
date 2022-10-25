# EUR-Lex-Sum: A Multi- and Cross-lingual Dataset for Long-form Summarization in the Legal Domain

Dennis Aumiller*, Ashish Chouhan*, and Michael Gertz  
Heidelberg University & SRH Hochschule Heidelberg  
contact us at: [`{aumiller, chouhan, gertz}@informatik.uni-heidelberg.de`](mailto:aumiller@informatik.uni-heidelberg.de)

**Find our dataset on the Huggingface Hub:** 🤗 [eur-lex-sum](https://huggingface.co/datasets/dennlinger/eur-lex-sum)    
The data card also provides further insight on the acquisition process (and some limitations) of the data. Please refer to the Huggingface Hub for more information.

A [pre-print](https://arxiv.org/abs/2210.13448) of our work is available; the work has been accepted at the main conference track of EMNLP 2022.

## Installation
Install all necessary dependencies by running `python3 -m pip install -r requirements.txt` after cloning this repository.

The provided repository provides code for the scraping process (`Scraping/`), as well as the analysis of our corpus (`Analysis/`) and final baseline experiments (`Baselines/`).

## Comparison of proposed dataset, i.e., EUR-Lex-Sum with Related Work
| Dataset Name        | Domain     | Number of Languages | Average Tokens in Reference Text | Average Tokens in the Summary text (in words) | Compression Ratio | Dataset              |
| :-------------------------: | :----------: | :--------: | :--------------------------------: | :---------------------------------------------: | :-----------------: | :--------------------: |
| [BillSum (US)](https://aclanthology.org/D19-5406/)        | Legal      | 1        | 1382                             | 2000 characters, Words are not considered as tokens     | -      | [🤗](https://huggingface.co/datasets/billsum) |
| [BillSum (CA)](https://aclanthology.org/D19-5406/)        | Legal      | 1        | 1684                             | 2000 characters, Words are not considered as tokens    | -      | [🤗](https://huggingface.co/datasets/billsum) |
| [Global Voices](https://aclanthology.org/D19-5411/)       | News       | 15       | 359                              | 51                                            | -      | [Paperswithcode](https://paperswithcode.com/dataset/global-voices)        |
| [WikiLingua](https://aclanthology.org/2020.findings-emnlp.360/)          | WikiHow    | 18       | 391                              | 39                                            | -      | [🤗](https://huggingface.co/datasets/wiki_lingua) |
| [Xwikis (comparable)](https://aclanthology.org/2021.emnlp-main.742/)      | Wikipedia  | 4        | 945                              | 77                                            | EN: -         | [🤗](https://huggingface.co/datasets/GEM/xwikis)                     |
| | | | | | DE: 17,44 | |
| | | | | | FR: 20,16 | |
| | | | | | CS: 15,12 | |
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
| [EUR-Lex-Sum](https://arxiv.org/abs/2210.13448) - Our Contribution        | Legal      | 24        | Refer to Table 5 in the Paper  | Refer to Table 5 in the Paper     | Refer to Table 5 in the Paper | [🤗](https://huggingface.co/datasets/dennlinger/eur-lex-sum) |


## Cite our work
If you use the dataset or otherwise use part of our work, please use the following citation for attribution:

```
@article{aumiller-etal-2022-eur,
author = {Aumiller, Dennis and Chouhan, Ashish and Gertz, Michael},
title = {{EUR-Lex-Sum: A Multi- and Cross-lingual Dataset for Long-form Summarization in the Legal Domain}},
journal = {CoRR},
volume = {abs/2210.13448},
eprinttype = {arXiv},
eprint = {2210.13448},
url = {https://arxiv.org/abs/2210.13448}
}
```
